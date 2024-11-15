from django import forms
from .models import AuthUser
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django import forms
from django.contrib.auth import authenticate
from django import forms 
from .models import AuthUser, Usuarios, Carrito
from django.utils import timezone
from django.contrib.auth.hashers import make_password

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir Contraseña", widget=forms.PasswordInput)
    email2 = forms.EmailField(label="Repetir Correo Electrónico")

    class Meta:
        model = AuthUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'birth_date', 'phone_number', 
            'gender'
        ]
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'birth_date': 'Fecha de Nacimiento',
            'phone_number': 'Número de Teléfono',
            'gender': 'Género',
        }
        widgets = {
            'birth_date': forms.SelectDateWidget(years=range(1900, timezone.now().year + 1)),
            'gender': forms.Select(choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email and email2 and email != email2:
            raise forms.ValidationError("Los correos electrónicos no coinciden")
        return email2

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos")
        if len(phone_number) != 12:
            raise forms.ValidationError("El número de teléfono debe tener 12 dígitos")
        return phone_number

    def clean_gender(self):
        gender = self.cleaned_data.get("gender")
        if gender not in ['M', 'F', 'O']:
            raise forms.ValidationError("Género no válido")
        return gender

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password1"])  # Encriptar la contraseña
        user.is_superuser = False  # Valor por defecto
        user.is_staff = False  # Cambia según tu lógica
        user.is_active = True  # Marcamos el usuario como activo
        user.date_joined = timezone.now()  # Fecha de registro
        if commit:
            user.save()

            # Crear la instancia del modelo Usuarios
            Usuarios.objects.create(
                id=user.id,  # Usamos el mismo ID que el de auth_user
                birth_date=self.cleaned_data.get("birth_date"),
                phone_number=self.cleaned_data.get("phone_number"),
                gender=self.cleaned_data.get("gender"),
                auth_user=user
            )
            Carrito.objects.create(
                usuario=user,
                fecha_creacion=timezone.now(),
                estado='abierto',  # Estado inicial del carrito
                total=0,  # Total inicial del carrito
                metodo_pago='Transbank',
                referencia_pago='webpay'
            )

        return user



from django import forms
from .models import AuthUser

class CustomLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre de usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}))


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Credenciales inválidas. Por favor intente nuevamente.")


from django import forms
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']





from django import forms
from .models import Direccion

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['region', 'comuna', 'destinatario', 'calle', 'numero', 'datos_adicionales']



from django import forms
from .models import AuthUser

class ActualizarPerfilForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ['birth_date', 'phone_number', 'gender']  # Solo los campos que se necesitan
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


from django import forms
from .models import Libro

class LibroForm(forms.ModelForm):
    imagen = forms.ImageField(required=False)  # Campo para subir la imagen

    class Meta:
        model = Libro
        fields = ['isbn', 'titulo', 'autor', 'categoria', 'descripcion', 'precio', 
                  'stock', 'formato', 'idioma', 'anio', 'num_paginas', 'encuadernacion', 
                  'dimensiones', 'imagen']  # Incluye el campo de imagen
        
from django import forms
from .models import LVentaU, Autor, Categoria

class LVentaUForm(forms.ModelForm):
    tipo_registro = forms.ChoiceField(
        choices=[('venta', 'Venta'), ('intercambio', 'Intercambio')],
        widget=forms.RadioSelect(attrs={'onchange': 'togglePrecioInput(this.value)'})
    )
    
    class Meta:
        model = LVentaU
        fields = ['isbn', 'titulo', 'autor', 'categoria', 'precio', 'stock', 'estado', 'descripcion', 'tipo_registro', 'imagen_url']
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'imagen_url': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'isbn': 'ISBN',
            'titulo': 'Título del Libro',
            'autor': 'Autor',
            'categoria': 'Categoría',
            'precio': 'Precio (CLP)',
            'stock': 'Stock',
            'estado': 'Estado',
            'descripcion': 'Descripción',
            'imagen_url': 'Imagen',
        }

    def clean_precio(self):
        tipo_registro = self.cleaned_data.get('tipo_registro')
        precio = self.cleaned_data.get('precio')
        if tipo_registro == 'venta' and (precio is None or precio <= 0):
            raise forms.ValidationError('El precio es obligatorio para el registro de tipo venta.')
        elif tipo_registro == 'intercambio':
            return 0  # Si es intercambio, devolver 0 como precio
        return precio
