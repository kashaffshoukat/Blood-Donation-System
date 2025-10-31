from django.shortcuts import render, redirect, reverse, get_object_or_404
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from django.contrib import messages 
from django.contrib.messages import constants as DEFAULT_MESSAGE_LEVELS


# --- Utility Function for Donor Check ---
def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

# --- Utility Function for Admin Check (NEW) ---
# Assuming Admin is either a staff member or in an 'ADMIN' group
def is_admin(user):
    return user.is_active and user.is_staff or user.groups.filter(name='ADMIN').exists() 


# --- Public View: Search for Approved Donors (NEW) ---
def public_donor_search_view(request):
    """
    Handles the public search for approved donors by blood group.
    
    Donors displayed must have an 'Approved' status and an active user account.
    """
    donors = []
    searched_bloodgroup = None
    
    # Check if a search query (bloodgroup) was provided in the URL parameters
    if 'bloodgroup' in request.GET:
        searched_bloodgroup = request.GET['bloodgroup'].strip()
        
        if searched_bloodgroup:
            # Filter Approved Donors by the selected Blood Group.
            # Assuming 'status' is a field on the Donor model to mark them as approved for public view.
            donors = models.Donor.objects.filter(
                bloodgroup__iexact=searched_bloodgroup, 
                user__is_active=True, 
                status__iexact='Approved' 
            ).select_related('user') # Fetch User data efficiently
        
        # Add a message if no results are found after searching
        if searched_bloodgroup and not donors:
            messages.info(request, f"No approved donors found for Blood Group: {searched_bloodgroup}.")
        
    context = {
        'donors': donors,
        'searched_bloodgroup': searched_bloodgroup,
    }
    
    # NOTE: This view expects the template 'donor/public_donor_search.html'
    return render(request, 'donor/public_donor_search.html', context)


# --- Existing View: Donor Signup (UPDATED) ---
def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    # Initialize mydict with the forms and the 'registered' flag
    mydict={'userForm':userForm,'donorForm':donorForm, 'registered': False} 
    
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            
            my_donor_group, created = Group.objects.get_or_create(name='DONOR')
            my_donor_group.user_set.add(user)
            
            # --- CHANGE MADE HERE ---
            # Set the flag to true and re-render the same page to show the success message
            mydict['registered'] = True
            return render(request,'donor/donorsignup.html',context=mydict)
        # If forms are invalid, fall through to re-render with errors
            
    return render(request,'donor/donorsignup.html',context=mydict)

# --- Existing View: Donor Dashboard (Ensured it's login_required) ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)

# --- Existing View: Display and Update Donor Profile ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def donor_profile_view(request):
    # Fetch the currently logged-in donor's data
    try:
        donor = models.Donor.objects.get(user=request.user)
    except models.Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor-dashboard') # Redirect to a safe page

    # Initialize forms with the current instance data
    user_form = forms.DonorUserForm(instance=request.user)
    donor_form = forms.DonorForm(instance=donor)

    if request.method == 'POST':
        # Re-initialize forms with POST data and current instance
        user_form = forms.DonorUserForm(request.POST, instance=request.user)
        donor_form = forms.DonorForm(request.POST, request.FILES, instance=donor)
        
        if user_form.is_valid() and donor_form.is_valid():
            user = user_form.save(commit=False)
            user.save()

            donor_obj = donor_form.save(commit=False)
            # Handle bloodgroup explicitly as it's a choice field
            donor_obj.bloodgroup=donor_form.cleaned_data['bloodgroup'] 
            donor_obj.save()
            
            messages.success(request, "Your profile has been updated successfully!")
            # Corrected redirect name to match urls.py
            return redirect('donor_profile_management') 
        else:
            messages.error(request, "Error updating profile. Please correct the errors below.")
    
    context = {
        'userForm': user_form,
        'donorForm': donor_form,
        'donor': donor,
    }
    return render(request, 'donor/donor_profile_management.html', context)


# --- Existing View: Delete Donor Profile ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def delete_donor_profile_view(request):
    user_to_delete = get_object_or_404(User, id=request.user.id)
    
    from django.contrib.auth import logout
    logout(request)
    
    user_to_delete.delete()
    
    messages.success(request, "Your account has been successfully deleted. Goodbye!")
    return redirect('/') # Redirect to the homepage

# --- Existing View: Donate Blood ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def donate_blood_view(request):
    donation_form=forms.DonationForm()
    if request.method=='POST':
        donation_form=forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate=donation_form.save(commit=False)
            blood_donate.bloodgroup=donation_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_donate.donor=donor
            blood_donate.save()
            messages.success(request, "Blood donation submitted successfully! Awaiting admin approval.")
            return redirect('donation-history') 
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form})

# --- Existing View: Donation History ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

# --- Existing View: Make Request ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            messages.success(request, "Request for blood submitted successfully! Awaiting admin approval.")
            return redirect('request-history') 
    return render(request,'donor/makerequest.html',{'request_form':request_form})

# --- Existing View: Request History ---
@login_required(login_url='donorlogin')
@user_passes_test(is_donor)
def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':blood_request})

# --- Existing ADMIN VIEW: DONOR DETAILS WITH CORRECT SEARCH FILTERING ---
@login_required(login_url='/admin/login')
@user_passes_test(is_admin)
def admin_view_donor_view(request):
    # 1. Get the search queries from the GET request, providing a default empty string
    query_bg = request.GET.get('blood_group', '').strip() 
    query_city = request.GET.get('city', '').strip()       

    donors = models.Donor.objects.all()
    
    # Start with an empty Q object
    filters = Q() 

    # 2. Check and build filters using the AND operator (&)
    if query_bg:
        # Filter by Blood Group: case-insensitive exact match
        filters &= Q(bloodgroup__iexact=query_bg) 
    
    if query_city:
        # Filter by City/Address: case-insensitive containment (like)
        filters &= Q(address__icontains=query_city) 

    # 3. Apply filters
    if filters:
        donors = donors.filter(filters)
        
    # 4. Check for no results and display an alert message
    if (query_bg or query_city) and not donors:
        # Construct the detailed message
        search_terms = []
        if query_bg:
            search_terms.append(f"Blood Group: {query_bg}")
        if query_city:
            search_terms.append(f"City: {query_city}")
        
        message = f"No donor profiles found matching: {', '.join(search_terms)}."
        # Use messages.error which maps to Bootstrap's 'danger' class by default
        messages.error(request, message)

        
    context = {
        'donors': donors,
    }
    
    return render(request, 'blood/admin_donor.html', context)