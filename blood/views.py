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
from donor import models as dmodels 
from patient import models as pmodels 
from donor import forms as dforms
from patient import forms as pforms
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages # ADDED FOR USER FEEDBACK

# Utility function to check if the user is a donor
def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

# Utility function to check if the user is a patient
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


# --- HOME VIEW (Public Facing Dashboard with Search) ---
def home_view(request):
    # --- Stock Initialization ---
    x=models.Stock.objects.all()
    
    if len(x)==0:
        bloodgroups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        for bg in bloodgroups:
            blood=models.Stock(bloodgroup=bg)
            blood.save()

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    
    # --- Get search parameters ---
    req_blood_group = request.GET.get('req_blood_group', '').strip()
    req_city = request.GET.get('req_city', '').strip()
    don_blood_group = request.GET.get('don_blood_group', '').strip()
    don_city = request.GET.get('don_city', '').strip()
    
    # --- Apply Filters ---
    approved_requests_query = models.BloodRequest.objects.filter(status='Approved')
    approved_donations_query = dmodels.BloodDonate.objects.filter(status='Approved')
    
    if req_blood_group:
        approved_requests_query = approved_requests_query.filter(bloodgroup__iexact=req_blood_group)
    if req_city:
        approved_requests_query = approved_requests_query.filter(request_by_patient__address__icontains=req_city)

    if don_blood_group:
        approved_donations_query = approved_donations_query.filter(bloodgroup__iexact=don_blood_group)
    if don_city:
        approved_donations_query = approved_donations_query.filter(donor__address__icontains=don_city)

    # Final fetch after filtering: last 15 items ordered by date
    approved_requests = approved_requests_query.order_by('-date')[:15]
    approved_donations = approved_donations_query.order_by('-date')[:15]

    # Build Context
    context = {
        'stocks': models.Stock.objects.all().order_by('bloodgroup'),
        'approved_requests': approved_requests,
        'approved_donations': approved_donations,
        'search_req_blood_group': req_blood_group,
        'search_req_city': req_city,
        'search_don_blood_group': don_blood_group,
        'search_don_city': don_city,
    }

    return render(request, 'blood/index.html', context)


# --- ROUTING VIEW AFTER LOGIN ---
def afterlogin_view(request):
    if is_donor(request.user):
        return redirect('donor/donor-dashboard')
    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        # Assumes non-donor/non-patient users are admins
        return redirect('admin-dashboard')


# --- NEW: ADMIN DASHBOARD VIEW (Fixes AttributeError) ---
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # Calculate Total Stock
    total_stock = models.Stock.objects.aggregate(Sum('unit'))['unit__sum'] or 0

    # Count Requests
    pending_request_count = models.BloodRequest.objects.filter(status='Pending').count()
    approved_request_count = models.BloodRequest.objects.filter(status='Approved').count()
    rejected_request_count = models.BloodRequest.objects.filter(status='Rejected').count()

    # Count Donations
    pending_donation_count = dmodels.BloodDonate.objects.filter(status='Pending').count()
    approved_donation_count = dmodels.BloodDonate.objects.filter(status='Approved').count()
    rejected_donation_count = dmodels.BloodDonate.objects.filter(status='Rejected').count()
    
    context = {
        'total_stock': total_stock,
        'pending_request_count': pending_request_count,
        'approved_request_count': approved_request_count,
        'rejected_request_count': rejected_request_count,
        'pending_donation_count': pending_donation_count,
        'approved_donation_count': approved_donation_count,
        'rejected_donation_count': rejected_donation_count,
    }
    
    return render(request, 'blood/admin_dashboard.html', context)


# --- CORRECTED: ADMIN BLOOD STOCK VIEW ---
@login_required(login_url='adminlogin')
def admin_blood_view(request):
    # 1. Handle POST Request (Form Submission for updating stock)
    if request.method == 'POST':
        bloodgroup = request.POST.get('bloodgroup')
        unit_str = request.POST.get('unit')

        # Basic Validation Check
        if not bloodgroup or bloodgroup == 'Choose Blood Group': 
            messages.error(request, "Please select a **Blood Group** to update.")
            return HttpResponseRedirect('/admin-blood')
            
        if not unit_str:
            messages.error(request, "Please enter the **unit quantity**.")
            return HttpResponseRedirect('/admin-blood')
            
        try:
            # CRITICAL STEP: Convert 'unit' to an integer
            unit = int(unit_str)
            
            # Find the Stock object
            stock = models.Stock.objects.get(bloodgroup=bloodgroup)
            
            # Update the stock unit (Add the new unit to the existing unit)
            stock.unit += unit 
            stock.save()
            
            messages.success(request, f"Successfully added {unit}ml of {bloodgroup} to stock.")
            
        except ValueError:
            messages.error(request, "Invalid unit value. Please enter a whole number.")
        
        except models.Stock.DoesNotExist:
            messages.error(request, f"Error: Stock for {bloodgroup} not found. Check initialization.")
            
        # Always redirect after POST to prevent double submission
        return HttpResponseRedirect('/admin-blood')
            
    # 2. Handle GET Request (Initial Page Load)
    stocks = models.Stock.objects.all().order_by('bloodgroup')
    
    # Prepare individual stock items for the template context
    context = {
        'A1': stocks.filter(bloodgroup='A+').first(),
        'B1': stocks.filter(bloodgroup='B+').first(),
        'O1': stocks.filter(bloodgroup='O+').first(),
        'AB1': stocks.filter(bloodgroup='AB+').first(),
        'A2': stocks.filter(bloodgroup='A-').first(),
        'B2': stocks.filter(bloodgroup='B-').first(),
        'O2': stocks.filter(bloodgroup='O-').first(),
        'AB2': stocks.filter(bloodgroup='AB-').first(),
    }
    
    return render(request, 'blood/admin_blood.html', context)

# --- OTHER ADMIN VIEWS (EXISTING) ---

@login_required(login_url='adminlogin')
def admin_donor_view(request):
    donors=dmodels.Donor.objects.all()
    return render(request,'blood/admin_donor.html',{'donors':donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(instance=donor)    
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)

@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return redirect('admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    patients=pmodels.Patient.objects.all()
    return render(request,'blood/admin_patient.html',{'patients':patients})

@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    patientForm=pforms.PatientForm(instance=patient)    
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)

@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests=models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request,'blood/admin_request_history.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_donation_view(request):
    donations=dmodels.BloodDonate.objects.all().filter(status='Pending')
    return render(request,'blood/admin_donation.html',{'donations':donations})

@login_required(login_url='adminlogin')
def update_approve_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    message=None
    bloodgroup=req.bloodgroup
    unit=req.unit
    try:
        stock=models.Stock.objects.get(bloodgroup=bloodgroup)
    except models.Stock.DoesNotExist:
        message="Stock entry for this blood group not found."
        req.save()
        requests=models.BloodRequest.objects.all().filter(status='Pending')
        return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

    if stock.unit >= unit:
        stock.unit=stock.unit-unit
        stock.save()
        req.status="Approved"
        
    else:
        message="Stock Does Not Have Enough Blood To Approve This Request, Only "+str(stock.unit)+" Unit Available"
    req.save()

    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

@login_required(login_url='adminlogin')
def update_reject_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    req.status="Rejected"
    req.save()
    return HttpResponseRedirect('/admin-request')

@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    stock=models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit=stock.unit+donation_blood_unit
    stock.save()

    donation.status='Approved'
    donation.save()
    return HttpResponseRedirect('/admin-donation')


@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.status='Rejected'
    donation.save()
    return HttpResponseRedirect('/admin-donation')

@login_required(login_url='adminlogin')
def admin_donation_history_view(request):
    donations=dmodels.BloodDonate.objects.all().exclude(status='Pending')
    return render(request,'blood/admin_donation_history.html',{'donations':donations})

@login_required(login_url='adminlogin')
def requested_blood_view(request):
    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/requested_blood.html',{'requests':requests})

@login_required(login_url='adminlogin')
def view_stock_view(request):
    stocks=models.Stock.objects.all().order_by('bloodgroup')
    return render(request,'blood/view_stock.html',{'stocks':stocks})

@login_required(login_url='adminlogin')
def blood_stock_view(request):
    stocks=models.Stock.objects.all().order_by('bloodgroup')
    return render(request,'blood/view_stock.html',{'stocks':stocks})