from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def confirm_reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Redefine a senha
            form.save()

            # Recupera o usuário
            user = form.user

            # Verifica se a nova senha é válida
            if user.check_password(form.cleaned_data['new_password1']):
                # Se a nova senha for válida, faça o login do usuário
                login(request, user)
                return redirect('perfil')

    else:
        form = PasswordResetForm()

    return render(request, 'password_reset_confirm.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            message = 'Usuário ou senha inválidos'
            return render(request, 'registration/login.html', {'message': message})
        
    return render(request, 'registration/login.html') 


@login_required
def logout_view(request):
    logout(request)
    return redirect('homepage')
