from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.auth.views import LoginView # Make sure this is imported if used elsewhere

# --- 1. SIGNUP VIEW ---
def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    
    # Initialize mydict with the forms and set 'registered' to False initially
    mydict={'userForm':userForm,'patientForm':patientForm, 'registered': False}
    
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            
            # Ensure the 'PATIENT' group exists before trying to add a user
            my_patient_group, created = Group.objects.get_or_create(name='PATIENT')
            my_patient_group.user_set.add(user)
            
            # Render the same template with 'registered': True to show the success card.
            mydict['registered'] = True
            return render(request,'patient/patientsignup.html',context=mydict)
        
    return render(request,'patient/patientsignup.html',context=mydict)


# --- 2. DASHBOARD VIEW (With Error Handling) ---
@login_required(login_url='patientlogin')
def patient_dashboard_view(request):
    try:
        # Safely try to fetch the Patient profile
        patient = models.Patient.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        # If the Patient profile doesn't exist, redirect to signup/profile creation
        return redirect('patientsignup')

    dict={
        'requestpending': bmodels.BloodRequest.objects.filter(request_by_patient=patient, status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.filter(request_by_patient=patient, status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.filter(request_by_patient=patient, status='Rejected').count(),
    }
   
    return render(request,'patient/patient_dashboard.html',context=dict)

# --- 3. MAKE REQUEST VIEW (With Error Handling) ---
@login_required(login_url='patientlogin')
def make_request_view(request):
    request_form=bforms.RequestForm() # This will now work
    
    # Safely get the patient object before proceeding
    try:
        patient = models.Patient.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        return redirect('patientsignup')

    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            blood_request.request_by_patient=patient
            blood_request.save()
            
            # Redirect to the list of requests
            return HttpResponseRedirect('my-request')  
            
    return render(request,'patient/makerequest.html',{'request_form':request_form})


# --- 4. MY REQUEST VIEW (With Error Handling) ---
@login_required(login_url='patientlogin')
def my_request_view(request):
    try:
        # Safely try to fetch the Patient profile
        patient = models.Patient.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        # If the Patient profile doesn't exist, redirect to signup
        return redirect('patientsignup')

    # If the patient exists, proceed with the request query
    blood_request=bmodels.BloodRequest.objects.filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})