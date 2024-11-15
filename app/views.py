from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
import requests
import json
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Problema
from django.utils import timezone
from django.contrib import messages
from .models import Problema, Respuesta
# Formularios personalizados
from .forms import CustomUserCreationForm, UserUpdateForm, ActualizarPerfilForm, CustomLoginForm

# Modelos
from .models import Direccion, Region, Comuna, Libro, Carrito, Carritoitem, AuthUser, Pedido,LIntercambio, Pedidoitem, Usuarios, Comentarios, Solicitudintercambio, Autor, Categoria, LVentaU

# Configuración de Webpay Plus
Transaction.default_integration_type = IntegrationType.TEST  # Usa IntegrationType.PRODUCTION en producción
Transaction.default_commerce_code = '597055555532'  # Código de comercio de integración
Transaction.default_api_key = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'  # Clave de API de integración




def base(request):
    username = request.user.id
    user = AuthUser.objects.get(id=username)
    categorias = Categoria.objects.all()
    data={
        'user':user,
        'categorias':categorias
    }


    return render(request, 'app/base.html', data)


from django.shortcuts import render, get_object_or_404
from .models import Libro, Categoria

def libros_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    libros = Libro.objects.filter(categoria=categoria)
    categorias = Categoria.objects.all()  # Para seguir mostrando todas las categorías en el sidebar
    return render(request, 'app/libros_por_categoria.html', {
        'categoria': categoria,
        'libros': libros,
        'categorias': categorias
    })






def libros_por_categoria(request, categoria_id):
    # Obtener la categoría seleccionada
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    # Obtener todos los libros asociados a esa categoría
    libros = Libro.objects.filter(categoria=categoria)
    
    return render(request, 'app/libros_por_categoria.html', {'categoria': categoria, 'libros': libros})




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Libro, LVentaU, Solicitudintercambio

@login_required
def home(request):
    user = request.user.id
    libros = Libro.objects.all()
    libros_vender = LVentaU.objects.filter(solicitud='aprobado', tipo_registro='venta')
    libros_intercambio = LVentaU.objects.filter(solicitud='aprobado', tipo_registro='intercambio')
    
    # Filtrar solicitudes pendientes del usuario autenticado y obtener IDs de libros
    solicitudes_pendientes = Solicitudintercambio.objects.filter(
        solicitante=user,
        estado='pendiente'
    ).values_list('libro_id', flat=True)  # Obtenemos solo los IDs de los libros con solicitudes pendientes

    # Obtener los libros del usuario para intercambio
    mis_libros_intercambio = LVentaU.objects.filter(usuario_id=user, tipo_registro='intercambio', solicitud='aprobado')

    return render(request, 'app/home.html', {
        'libros': libros,
        'intercambios': libros_intercambio,
        'libros_vender': libros_vender,
        'solicitudes_pendientes': list(solicitudes_pendientes),  # Convertir a lista para usar en el template
        'mis_libros_intercambio': mis_libros_intercambio
    })



import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Libro
from .forms import LibroForm
from .utils import upload_image_to_supabase  # Asegúrate de que esta función esté bien configurada

def actualizar_libro_con_imagen(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == "POST":
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            imagen = form.cleaned_data['imagen']
            print(f'imagen: {imagen}')
            if imagen:
                # Subir imagen a Supabase y obtener la URL
                imagen_url = upload_image_to_supabase(imagen, f"libros/{libro_id}.jpg")
                libro.imagen_url = imagen_url  # Asocia la URL de la imagen al libro
            form.save()
            return redirect('home')  # Redirige al catálogo o a donde prefieras

    else:
        form = LibroForm(instance=libro)
    
    return render(request, 'app/editar_libro.html', {'form': form, 'libro': libro})











from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend  # Importa el backend

def registro(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guardar el nuevo usuario

            # Especifica el backend de Django para el inicio de sesión
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  
            
            messages.success(request, "Registro exitoso. Has iniciado sesión.")
            return redirect('home')  # Redirigir a la página de inicio
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'app/registro.html', {'form': form})




def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Iniciar sesión
                messages.success(request, "Inicio de sesión exitoso.")
                return redirect('home')  # Redirigir a la página de inicio
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = CustomLoginForm()  # Crear una instancia vacía del formulario

    return render(request, 'app/login.html', {'form': form})



def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('login')  # Redirige al usuario a la página de inicio de sesión



@login_required
def verificar_datos_adicionales(request):
    auth_user_id = request.user.id  # Obtiene el ID del usuario autenticado
    try:
        user = Usuarios.objects.get(auth_user_id=auth_user_id)  # Busca el registro en Usuarios
        if not user.birth_date or not user.gender or not user.phone_number:
            return redirect('actualizar_perfil')  # Si falta algún dato, redirige a actualizar
    except Usuarios.DoesNotExist:
        return redirect('actualizar_perfil')  # Si no existe el registro, redirige a actualizar

    return redirect('home')  # Si todo está correcto, redirige al home


@login_required
def actualizar_perfil(request):

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        phone_number = request.POST.get('telefono')
        birth_date = request.POST.get('fecha_nacimiento')
        gender = request.POST.get('genero')
        
        # Obtener la dirección existente
        usuario_id = AuthUser.objects.get(id=usuario_id)



        # Guardar la dirección en la base de datos
        nuevo_usuario = Usuarios.objects.create(
            id=usuario_id.id,  # Aquí se pasa el valor del ID numérico
            phone_number=phone_number,
            birth_date=birth_date,
            gender=gender,
            auth_user=usuario_id,  # Aquí se mantiene el objeto completo
        )

            
        nuevo_usuario.save()
        messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
        Carrito.objects.create(
            usuario=usuario_id,
            fecha_creacion=timezone.now(),
            estado='abierto',  # Estado inicial del carrito
            total=0,  # Total inicial del carrito
            metodo_pago='Transbank',
            referencia_pago='webpay'
        )
        return redirect('home')


    return render(request, 'app/actualizar_perfil.html')












@login_required
def profile_view(request):
    user = request.user.id  # Esto ya es el objeto AuthUser
    regiones = Region.objects.all()

    try:

        direcciones = Direccion.objects.get(usuario=user)  # Usa filter para obtener todas las direcciones
    except Direccion.DoesNotExist:
        direcciones = None  # Manejar caso sin direcciones
    usuario = AuthUser.objects.get(id=user)
    usuarios = Usuarios.objects.get(id=user)

    context = {
        'regiones': regiones,
        'direcciones': direcciones,
        'usuario': usuario,
        'usuarios': usuarios
    }
    return render(request, 'app/profile.html', context)



@login_required
def actualizar_user(request):
    user = request.user

    if request.method == 'POST':
        # Obtener los datos enviados por el formulario
        first_name = request.POST.get('nombre')
        email = request.POST.get('email')
        phone_number = request.POST.get('telefono')
        birth_date = request.POST.get('fecha_nacimiento')
        usuarios = Usuarios.objects.get(id=user.id)
        # Actualizar los campos del usuario autenticado
        try:
            user.first_name = first_name
            user.email = email
            usuarios.phone_number = phone_number
            usuarios.birth_date = birth_date
            # Guardar cambios
            user.save()
            usuarios.save()

            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('profile')

        except Exception as e:
            messages.error(request, 'Error al actualizar el perfil.')

    # Si es una petición GET, mostrar el perfil con los datos actuales
    return render(request, 'app/profile.html', {'user': user})









def registrar_direccion(request):
    user = request.user

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id', '')  # Opcional
        region_id = request.POST['region_id']
        comuna_id = request.POST['comuna_id']
        destinatario = request.POST['destinatario']
        calle = request.POST['calle']
        numero = request.POST.get('numero', '')  # Opcional
        datos_adicionales = request.POST.get('datos_adicionales', '')  # Opcional

        # Guardar la dirección en la base de datos
        nueva_direccion = Direccion.objects.create(
            usuario=usuario_id,  # Aquí se está pasando el objeto AuthUser
            region_id=region_id,
            comuna_id=comuna_id,
            destinatario=destinatario,
            calle=calle,
            numero=numero,
            datos_adicionales=datos_adicionales
        )
        nueva_direccion.save()

        # Redireccionar o mostrar un mensaje de éxito
        return redirect('profile')  # Ajusta esto según tu URL de perfil

    # Si es GET, muestra el formulario con las regiones disponibles
    regiones = Region.objects.all()
    direcciones = Direccion.objects.filter(usuario=request.user)  # Filtra las direcciones del usuario

    return render(request, 'app/profile.html', {'regiones': regiones, 'direcciones': direcciones})

def registrar_direccion2(request):
    user = request.user

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id', '')  # Opcional
        region_id = request.POST['region_id']
        comuna_id = request.POST['comuna_id']
        destinatario = request.POST['destinatario']
        calle = request.POST['calle']
        numero = request.POST.get('numero', '')  # Opcional
        datos_adicionales = request.POST.get('datos_adicionales', '')  # Opcional

        # Guardar la dirección en la base de datos
        nueva_direccion = Direccion.objects.create(
            usuario=usuario_id,  # Aquí se está pasando el objeto AuthUser
            region_id=region_id,
            comuna_id=comuna_id,
            destinatario=destinatario,
            calle=calle,
            numero=numero,
            datos_adicionales=datos_adicionales
        )
        nueva_direccion.save()

        # Redireccionar o mostrar un mensaje de éxito
        return redirect('confirmacion_direccion')  # Ajusta esto según tu URL de perfil

    # Si es GET, muestra el formulario con las regiones disponibles
    regiones = Region.objects.all()
    direcciones = Direccion.objects.filter(usuario=request.user)  # Filtra las direcciones del usuario

    return render(request, 'app/confirmacion_direccion.html', {'regiones': regiones, 'direcciones': direcciones})





@login_required
def actualizar_direccion(request):
    if request.method == 'POST':
        region_id = request.POST.get('region_id')
        comuna_id = request.POST.get('comuna_id')
        destinatario = request.POST.get('destinatario')
        
        datos_adicionales = request.POST.get('datos_adicionales')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero')
        direccion_id = request.POST.get('direccion_id')

        # Obtener la dirección existente
        direccion = Direccion.objects.get(usuario=direccion_id)
        region_id = request.POST.get('region_id')
        comuna_id = request.POST.get('comuna_id')

        # Obtén la instancia de Region y Comuna a partir del ID
        region = get_object_or_404(Region, pk=region_id)
        comuna = get_object_or_404(Comuna, pk=comuna_id)
        # Actualizar los campos
        direccion.calle = calle
        direccion.numero = numero
        direccion.destinatario = destinatario
        direccion.region = region
        direccion.comuna = comuna
        direccion.datos_adicionales = datos_adicionales

        # Guardar cambios
        direccion.save()

        return redirect('profile')  # Redirigir al perfil después de actualizar

    return redirect('profile')


@login_required
def actualizar_direccion2(request):
    if request.method == 'POST':
        region_id = request.POST.get('region_id')
        comuna_id = request.POST.get('comuna_id')
        destinatario = request.POST.get('destinatario')

        datos_adicionales = request.POST.get('datos_adicionales')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero')
        direccion_id = request.POST.get('direccion_id')

        # Obtener la dirección existente
        direccion = Direccion.objects.get(usuario=direccion_id)
        region_id = request.POST.get('region_id')
        comuna_id = request.POST.get('comuna_id')

        # Obtén la instancia de Region y Comuna a partir del ID
        region = get_object_or_404(Region, pk=region_id)
        comuna = get_object_or_404(Comuna, pk=comuna_id)
        # Actualizar los campos
        direccion.calle = calle
        direccion.numero = numero
        direccion.destinatario = destinatario
        direccion.region = region
        direccion.comuna = comuna
        direccion.datos_adicionales = datos_adicionales

        # Guardar cambios
        direccion.save()

        return redirect('confirmacion_direccion')  # Redirigir al perfil después de actualizar

    return redirect('confirmacion_direccion')




def obtener_comunas(request, region_id):
    comunas = Comuna.objects.filter(region_id=region_id).values('id', 'nombre')
    return JsonResponse(list(comunas), safe=False)















"""                                                      Carrito de compras                                                """



def carrito(request):
    items = Carritoitem.objects.all()
    libro = Libro.objects.get(isbn=items.libro)
    
    data = {
        'items':items,
        'libro':libro
        
    }
    return render(request, 'app/carrito.html', data)



@login_required
def agregar_al_carrito(request, libro_id):
    usuario = request.user.id
    usuario = AuthUser.objects.get(id=usuario)
    libro = get_object_or_404(Libro, id=libro_id)  # Usamos get_object_or_404 para validar que existe
    carrito = Carrito.objects.filter(usuario=usuario, estado='abierto').first()

    if not carrito:
        carrito = Carrito.objects.create(
            usuario=usuario,
            fecha_creacion=timezone.now(),
            estado='abierto',
        )

    carrito.save()

    # Verificamos si ya está en el carrito
    item, item_created = Carritoitem.objects.get_or_create(
        carrito=carrito,
        libro=libro,
        defaults={
            'cantidad': 1,
            'precio_total': libro.precio,
            'descuento': 0
        }
    )

    if not item_created:
        # Validamos que no se agregue más cantidad de la disponible en stock
        if item.cantidad < libro.stock:
            item.cantidad += 1
            item.precio_total += libro.precio
            item.save()
        else:
            messages.error(request, f'No puedes agregar más de {libro.stock} unidades de "{libro.titulo}".')

    # Actualizamos el total del carrito
    carrito.total = sum(i.precio_total for i in Carritoitem.objects.filter(carrito=carrito))
    carrito.save()

    messages.success(request, f'El libro "{libro.titulo}" ha sido agregado al carrito.')
    return redirect('home')
@login_required
def carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user.id, estado='abierto').first()

    if not carrito:
        items = []
        total = 0
    else:
        items = Carritoitem.objects.filter(carrito=carrito)
        total = carrito.total

    data = {
        'items': items,
        'total': total,
        'envio': 2000,  # Puedes ajustar este valor
        'total_final': total + 2000  # Total con el valor de envío incluido
    }
    return render(request, 'app/carrito.html', data)

@login_required
def eliminar_del_carrito(request, item_id):
    producto = get_object_or_404(Carritoitem, id=item_id)
    producto.delete()

    # Opcional: recalcular el total del carrito después de la eliminación
    carrito = producto.carrito
    carrito.total = sum(item.precio_total for item in Carritoitem.objects.filter(carrito=carrito))
    carrito.save()

    messages.success(request, "El producto ha sido eliminado del carrito correctamente.")
    return redirect('carrito')



@login_required
def actualizar_cantidad(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        nueva_cantidad = int(request.POST.get('cantidad'))

        try:
            item = Carritoitem.objects.get(id=item_id)
            if nueva_cantidad <= item.libro.stock:  # Verificar si hay suficiente stock
                item.cantidad = nueva_cantidad
                item.precio_total = item.libro.precio * nueva_cantidad
                item.save()

                # Actualizar el total del carrito
                carrito = item.carrito
                carrito.total = sum(i.precio_total for i in Carritoitem.objects.filter(carrito=carrito))
                carrito.save()

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'No hay suficiente stock'}, status=400)
        except Carritoitem.DoesNotExist:
            return JsonResponse({'error': 'El item no existe'}, status=404)



"""------------------------------------------------------Integracion de pago----------------------------------------------------------"""



@login_required
def confirmacion_direccion(request):
    user = request.user.id  # Esto ya es el objeto AuthUser
    regiones = Region.objects.all()
    itmescarrito = Carritoitem.objects.filter(carrito=user)
    
    try:

        direcciones = Direccion.objects.get(usuario=user)  # Usa filter para obtener todas las direcciones
    except Direccion.DoesNotExist:
        direcciones = None  # Manejar caso sin direcciones
    usuario = AuthUser.objects.get(id=user)

    context = {
        'regiones': regiones,
        'direcciones': direcciones,
        'usuario': usuario,
        'itmescarrito': itmescarrito,
    }
    return render(request, 'app/confirmacion_direccion.html', context)









'-----------------se asigan la direccion del usuario al carrito, se rescata el monto a pagar y se genera la integracion con webpay---------------           '



def iniciar_pago(request):
    usuario = request.user  # Ya es una instancia de AuthUser, no uses .id aquí
    usuario = AuthUser.objects.get(username=usuario.username)  # Obtén solo un usuario
    usuario = usuario.id
    carrito = Carrito.objects.filter(usuario=usuario, estado='abierto').first()
    # Verificar si el usuario tiene una dirección registrada
    direccion = Direccion.objects.filter(usuario=usuario).first()
    if direccion:
        comuna_nombre = Comuna.objects.get(id=direccion.comuna.id).nombre
        region_nombre = Region.objects.get(id=direccion.region.id).nombre
        direccion_envio = f"{direccion.calle}, {direccion.numero}, {comuna_nombre}, {region_nombre}"
    else:
        direccion_envio = None  # Si no hay dirección, lo dejamos como None

    # Crear un nuevo carrito para el usuario con la dirección si existe
    carrito.direccion_envio = direccion_envio
    carrito.save()  # Guardar los cambios


    if not carrito:
        messages.error(request, "No tienes productos en el carrito.")
        return redirect('carrito')

    # Obtener el total del carrito sumando el precio_total de cada item
    total_amount = Carritoitem.objects.filter(carrito=carrito).aggregate(total=Sum('precio_total'))['total']

    if not total_amount or total_amount <= 0:
        messages.error(request, "El monto total es inválido.")
        return redirect('ver_carrito')



    # Crear un identificador único para la orden y la sesión
    buy_order = "dasdsadasdsf"  # Puedes usar usuario.id aquí
    session_id = f"session_{usuario}"
    amount = total_amount
    return_url = request.build_absolute_uri('confirmar_pago')  # Reemplaza con tu URL de retorno

    # Crear la transacción en Webpay
    transaction = Transaction()
    response = transaction.create(buy_order, session_id, amount, return_url)

    if response:
        token = response['token']
        url = response['url']
        return redirect(f"{url}?token_ws={token}")
    else:
        messages.error(request, "Error iniciando el pago con Webpay.")
        return redirect('carrito')






def confirmar_pago(request):
    token_ws = request.GET.get('token_ws')

    if not token_ws:
        messages.error(request, "El pago no se completó correctamente.")
        return redirect('carrito')

    try:
        transaction = Transaction()
        response = transaction.commit(token_ws)

        if response['status'] == 'AUTHORIZED':
           return orden_compra(request)
        else:
            messages.error(request, "El pago fue rechazado.")
            return redirect('profile')
    except Exception as e:  # Captura cualquier excepción
        messages.error(request, f"Error procesando el pago: {e}")
        return redirect('profile')





 
'-------------------------------Se ingresan valores a itemspedido y pedido y se muestra la informacion del pedido-----------------------------              '
def generar_numero_unico():
    while True:
        # Generar un número aleatorio de 6 dígitos
        numero = random.randint(100000, 999999)
        # Verificar si ya existe un pedido con ese número
        if not Pedido.objects.filter(n_orden_despacho=numero).exists():
            return numero

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import AuthUser, Carrito, Carritoitem, Pedido, Pedidoitem, Usuarios, Direccion, Comuna, Region

def orden_compra(request):
    # Crear el pedido en tu sistema
    usuario = request.user  # Ya es una instancia de AuthUser, no uses .id aquí
    usuario = AuthUser.objects.get(username=usuario.username)  # Obtén solo un usuario
    usuario = usuario.id
    carrito = Carrito.objects.get(usuario=usuario, estado='abierto')
    # Obtener el carrito abierto del usuario
    # Generar número único de orden de despacho
    n_espacho = generar_numero_unico()

    direccion = Direccion.objects.filter(usuario=usuario).first()
    if direccion:
        comuna_nombre = Comuna.objects.get(id=direccion.comuna.id).nombre
        region_nombre = Region.objects.get(id=direccion.region.id).nombre
        direccion_envio = f"{direccion.calle}, {direccion.numero}, {comuna_nombre}, {region_nombre}"
    else:
        direccion_envio = None  # Si no hay dirección, lo dejamos como None

    # Crear un nuevo pedido con el número de orden de despacho
    try:

        pedido = Pedido.objects.create(
            usuario=AuthUser.objects.get(id=usuario),
            precio_total=carrito.total,
            fecha_creacion=timezone.now(),
            completado=1,
            n_orden_despacho=n_espacho,
            direccion_envio=direccion_envio,

        )

        print(f"Pedido guardado correctamente: {pedido}, ID: {pedido.id}")
    except Exception as e:
        print(f"Error al guardar el pedido: {str(e)}")
    

        # Crear los items del pedido
    for item in Carritoitem.objects.filter(carrito=carrito.id):
        libro = item.libro

        # Descontar stock del libro
        if libro.stock >= item.cantidad:
            libro.stock -= item.cantidad
            libro.save()  # Guardar los cambios en la base de datos
        else:
            messages.error(request, f"Stock insuficiente para el libro {libro.titulo}.")
            return redirect('carrito')
        try:
            precio = item.cantidad * libro.precio
            # Crear cada Pedidoitem individualmente
            pedidoitem= Pedidoitem.objects.create(
                pedido_id=n_espacho,  # Usar la instancia de Pedido guardada
                libro=libro,
                cantidad=item.cantidad,
                precio_total=precio,
                direccion_envio=direccion_envio,
            )

        except Exception as e:
            print(f"Error al guardar los Pedidoitems create: {str(e)}")  # Registrar el error en consola
            messages.error(request, "Ocurrió un error al crear los items del pedido.")
            return redirect('carrito')
        # Intentar crear los Pedidoitem en la base de datos


    # Limpiar el carrito
    pedido_id=n_espacho,  # Usar la instancia de Pedido guardada
    libro=libro,
    cantidad=item.cantidad,
    precio_total=precio,
    direccion_envio=direccion_envio,
            
    print(f"Pedido guardado correctamente: {pedidoitem}, ID: {pedido_id}, libro: {libro}, precio_total: {precio_total}, direccion_envio: {direccion_envio}")


    Carritoitem.objects.filter(carrito=carrito).delete()
    carrito.estado = 'finalizado'
    carrito.save()



        # Crear un nuevo carrito para el usuario
    Carrito.objects.create(
        usuario= AuthUser.objects.get(id=usuario)  ,# Obtén solo un usuario,
        estado='abierto',
        fecha_creacion=timezone.now(),
        total = 0
    )
    usuarios = Usuarios.objects.get(id=usuario)

    nombre_cliente = AuthUser.objects.get(id=usuario)  # Obtén solo un usuario
    correo_cliente = AuthUser.objects.get(id=usuario)  # Obtén solo un usuario
    print(f'nombre cliente: {nombre_cliente.first_name}, correo cliente: {correo_cliente.email}, {usuarios.phone_number}')
    data = {

        'pedido_id_item': pedido_id,
        'libro_item': libro,
        'precio_total_item':precio_total,
        'direccion_envio_item':direccion,
        'usuarios':usuarios

    }
    seguimiento_data = {
        'id_orden': pedido_id[0] if isinstance(pedido_id, tuple) else pedido_id,
        'estado_envio': 'Pedido Ingresado',
        'metodo_envio': 'normal',
        'nombre_cliente': nombre_cliente.first_name,
        'correo_cliente': correo_cliente.email,
        'telefono_cliente': usuarios.phone_number,
        'direccion_envio': direccion_envio[0] if isinstance(direccion_envio, tuple) else direccion_envio,
        'cantidad': 1,
        'total': precio_total[0] if isinstance(precio_total, tuple) else precio_total
    }


    # Obtener la URL completa del endpoint `AgregarVenta` dentro de Django
    # Enviar datos a la API secundaria
    seguimiento_api_url = request.build_absolute_uri(reverse('agregar_venta'))
    
    try:
        response = requests.post(seguimiento_api_url, json=seguimiento_data, timeout=30, verify=False)
        
        # Verificar si el código de estado es 201 (creado)
        if response.status_code == 201:
            resultado = response.json()
            
            if resultado == 1:
                # Redirigir a la página de confirmación de compra si la inserción fue exitosa
                messages.success(request, "Pago exitoso, comenzaremos con el despacho de tu producto.")
                return render(request, 'app/orden_compra.html', data)
            elif resultado == 0:
                messages.warning(request, "Este pedido ya estaba registrado en el sistema de seguimiento.")
                return redirect('carrito')
        else:
            # Error en la solicitud, muestra mensaje de error y redirige al carrito
            messages.error(request, "Error en la solicitud al registrar el pedido.")
            return redirect('carrito')
    
    except requests.RequestException as e:
        # Manejo de excepciones en caso de error de conexión o tiempo de espera
        print(f"Error en la solicitud: {e}")
        messages.error(request, "Error al conectar con el servicio de seguimiento.")
        return redirect('carrito')

    # Redirige al carrito si por alguna razón no se manejó otra redirección
    return redirect('carrito')

"""--------------------------------------------------------------------Integracion de despacho-------------------------------------------------------------------------"""




def seguimiento(request):
    if request.method == "POST":
        id_seguimiento = request.POST.get('id_seguimiento')
        estado = obtener_estado_seguimiento(id_seguimiento)

        data = {
            'estado': estado,
        }

        return render(request, 'app/seguimiento.html', data)

    return render(request, 'app/seguimiento.html')


def obtener_estado_seguimiento(id_seguimiento):
    # Construye la URL de la API usando reverse para obtener la ruta
    seguimiento_api_url = reverse('estado_seguimiento')

    # Agrega el dominio si necesitas una URL completa
    seguimiento_api_url = f'http://127.0.0.1:8000{seguimiento_api_url}'

    # Datos a enviar a la API
    seguimiento_data = {
        'id_orden': id_seguimiento
    }

    try:
        # Realiza la solicitud POST a la API
        response = requests.post(seguimiento_api_url, json=seguimiento_data, timeout=30, verify=False)
        response.raise_for_status()  # Lanza un error si el código de estado no es 2xx

        # Verifica la respuesta y devuelve el estado si es exitoso
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                estado = response.json().get('estado_envio', 'Estado no encontrado')
                return estado
            else:
                return response.text
        else:
            return "No se pudo obtener el estado"
    except requests.RequestException as e:
        # Manejo de errores de conexión o de la solicitud
        print(f"Error al conectar con la API: {e}")
        return "Error al conectar con el servidor"





def pedidos(request):
    # Obtener los pedidos del usuario actual
    user = request.user
    user = user.id
    pedidos = Pedido.objects.filter(usuario=user).order_by('-fecha_creacion')

    # Agregar los items de cada pedido
    for pedido in pedidos:
        pedido.items = Pedidoitem.objects.filter(pedido_id=pedido.n_orden_despacho)

    # Preparar los datos para la plantilla
    data = {
        'pedidos': pedidos
    }
    
    return render(request, 'app/pedidos.html', data)






"""-------------------------------------------------------Funciones de usuario---------------------------------------------------------------"""

@login_required
def Registrar_libro_Intercambio(request):
    user = request.user
    user = user.id
    libros = LIntercambio.objects.filter(usuario=user)
    if request.method == 'POST':
        # Obtener los datos del formulario
        isbn = request.POST.get('isbn')
        titulo = request.POST.get('titulo')
        autor_id = request.POST.get('autor')
        categoria_id = request.POST.get('categoria')
        precio = request.POST.get('precio')
        descripcion = request.POST.get('descripcion')
        estado = 'Disponible'  # Estado predeterminado al registrar el libro
        stock = 1  # El stock inicial podría ser 1 por defecto
        solicitud = 'pendiente'
        
        try:
            # Obtener el autor y la categoría por su ID
            autor = Autor.objects.get(id=autor_id)
            categoria = Categoria.objects.get(id=categoria_id)
            usuario = AuthUser.objects.get(id=user)
        except (Autor.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, 'El autor o la categoría seleccionada no existe.')
            return redirect('Registrar_libro_Intercambio')

        # Crear un nuevo objeto de libro de intercambio
        nuevo_libro = LIntercambio.objects.create(
            isbn=isbn,
            titulo=titulo,
            autor=autor,  # Ahora pasamos una instancia de Autor
            categoria=categoria,  # Ahora pasamos una instancia de Categoria
            precio=precio,
            descripcion=descripcion,
            estado=estado,
            stock=stock,
            usuario=usuario, # Asignar el libro al usuario autenticado
            solicitud=solicitud
        )
        
        messages.success(request, 'El libro ha sido registrado exitosamente para intercambio.')
        return redirect('Registrar_libro_Intercambio')  # Redirigir a la misma página o donde desees

    # Si es GET, mostrar el formulario con las categorías y autores disponibles
    autores = Autor.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'app/Registrar_libro_Intercambio.html', {'autor': autores, 'categoria': categorias, 'libros':libros})



def actualizar_libro_con_imagen(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == "POST":
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            imagen = form.cleaned_data['imagen']
            print(f'imagen: {imagen}')
            if imagen:
                # Subir imagen a Supabase y obtener la URL
                imagen_url = upload_image_to_supabase(imagen, f"libros/{libro_id}.jpg")
                libro.imagen_url = imagen_url  # Asocia la URL de la imagen al libro
            form.save()
            return redirect('home')  # Redirige al catálogo o a donde prefieras

    else:
        form = LibroForm(instance=libro)
    
    return render(request, 'app/editar_libro.html', {'form': form, 'libro': libro})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import requests
from .models import LVentaU, Solicitudintercambio, Autor, Categoria, AuthUser
from .utils import upload_image_to_supabase  # Asegúrate de tener la función de carga de imagen en utils.py
import uuid

@login_required
def Registrar_libro_usuario(request):
    user = request.user
    user_id = user.id
    libros = LVentaU.objects.filter(usuario=user_id)
    solicitudes = Solicitudintercambio.objects.filter(destinatario=request.user.id, estado='pendiente')

    if request.method == 'POST':
        # Obtener los datos del formulario
        isbn = request.POST.get('isbn')
        titulo = request.POST.get('titulo')
        autor_id = request.POST.get('autor')
        categoria_id = request.POST.get('categoria')
        tipo_registro = request.POST.get('tipo_registro')
        precio = float(request.POST.get('precio')) if tipo_registro == 'venta' else 0  # Precio es 0 si es intercambio
        descripcion = request.POST.get('descripcion')
        estado = 'Disponible'
        stock = 1
        solicitud = 'pendiente'
        imagen = request.FILES.get('imagen')  # Obtener la imagen cargada
        print(f'imagen: {imagen}')
        try:
            autor = Autor.objects.get(id=autor_id)
            categoria = Categoria.objects.get(id=categoria_id)
            usuario = AuthUser.objects.get(id=user_id)
        except (Autor.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, 'El autor o la categoría seleccionada no existe.')
            return redirect('Registrar_libro_usuario')
        unique_id = uuid.uuid4()

        if imagen:
            # Subir imagen a Supabase y obtener la URL
            imagen_url = upload_image_to_supabase(imagen, f"libros/{tipo_registro}_{unique_id}.jpg")
            imagen_url = imagen_url  # Asocia la URL de la imagen al libro

        else:
            return redirect('home')  # Redirige al catálogo o a donde prefieras




        # Crear el objeto de libro
        nuevo_libro = LVentaU.objects.create(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            categoria=categoria,
            precio=precio,
            tipo_registro=tipo_registro,
            descripcion=descripcion,
            estado=estado,
            stock=stock,
            usuario=usuario,
            solicitud=solicitud,
            imagen_url=imagen_url  # Guardar la URL de la imagen cargada
        )

        if tipo_registro == 'venta':
            messages.success(request, 'El libro ha sido registrado exitosamente para venta.')
        else:
            messages.success(request, 'El libro ha sido registrado exitosamente para intercambio.')

        return redirect('Registrar_libro_usuario')
    solicitudes_enviadas = Solicitudintercambio.objects.filter(solicitante=user_id)
    autores = Autor.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'app/Registrar_libro_usuario.html', {'autor': autores, 'categoria': categorias, 'libros': libros, 'solicitudes':solicitudes,'solicitudes_enviadas':solicitudes_enviadas}, )








from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import LVentaU, Solicitudintercambio
from django.contrib.auth.decorators import login_required

@login_required
def eliminar_libro_usuario(request, libro_id):
    # Obtener el libro del usuario actual
    libro = get_object_or_404(LVentaU, id=libro_id, usuario_id=request.user.id)

    # Buscar cualquier solicitud de intercambio relacionada con el libro, si existe
    solicitud = Solicitudintercambio.objects.filter(libro_id=libro_id).first()  # Usar .first() para obtener solo una, o None si no existe

    try:
        # Eliminar la solicitud si existe
        if solicitud:
            solicitud.delete()
        
        # Eliminar el libro
        libro.delete()
        
        messages.success(request, "El libro ha sido eliminado exitosamente.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar el libro: {e}")

    # Redirigir a la misma página o a la lista de libros del usuario
    return redirect('Registrar_libro_usuario')







import requests
from django.http import JsonResponse

def buscar_libro_open_library(request):
    query = request.GET.get('query', '').strip()
    libros = []

    if query:
        url = f"https://openlibrary.org/search.json?q={query}&limit=10"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            for doc in data.get('docs', []):
                libro = {
                    'titulo': doc.get('title', 'Título no disponible'),
                    'autor': doc.get('author_name', ['Autor no disponible'])[0] if doc.get('author_name') else 'Autor no disponible',
                    'isbn': doc.get('isbn', ['ISBN no disponible'])[0] if doc.get('isbn') else 'ISBN no disponible',
                    'anio_publicacion': doc.get('first_publish_year', 'Año no disponible'),
                    'imagen_url': f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-L.jpg" if doc.get('cover_i') else 'https://via.placeholder.com/150'
                }
                libros.append(libro)

        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con Open Library API: {e}")
            return JsonResponse({'error': 'Error al conectar con Open Library API'}, status=500)

    return JsonResponse({'libros': libros})








def libro_detalle(request, libro_id):
    libro = Libro.objects.get(id=libro_id)
    comentarios = Comentarios.objects.filter(libro=libro).order_by('-fecha')
    user = request.user
    user = user.id
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comentario_texto = request.POST.get('comment')
        usuario = AuthUser.objects.get(id=user)

        # Crear un nuevo comentario solo si el usuario está autenticado
        if request.user.is_authenticated:
            nuevo_comentario = Comentarios.objects.create(
                libro=libro,
                usuario=usuario,
                calificacion=rating,
                comentario=comentario_texto,
                fecha=timezone.now()  # Aquí está el campo correcto
            )
            nuevo_comentario.save()

            return redirect('libro_detalle', libro_id=libro_id)

    data = {
        'libro': libro,
        'comentarios': comentarios
    }
    return render(request, 'app/libro_detalle.html', data)



@login_required
def evaluar_solicitudes(request):
    solicitudes = Solicitudintercambio.objects.filter(destinatario=request.user, estado='pendiente')

    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')
        solicitud = get_object_or_404(Solicitudintercambio, id=solicitud_id)

        if accion == 'aceptar':
            solicitud.estado = 'aceptada'
            messages.success(request, "Solicitud aceptada.")
        elif accion == 'rechazar':
            solicitud.estado = 'rechazada'
            messages.success(request, "Solicitud rechazada.")

        solicitud.save()
        return redirect('evaluar_solicitudes')

    return render(request, 'app/evaluar_solicitudes.html', {'solicitudes': solicitudes})





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import LVentaU, Solicitudintercambio, AuthUser
from django.contrib import messages

@login_required
def solicitar_intercambio(request, libro_id):
    libro = get_object_or_404(LVentaU, id=libro_id)
    solicitante = AuthUser.objects.get(id=request.user.id)
    destinatario = libro.usuario

    # Condición 1: Verificar que el solicitante no sea el propietario del libro
    if solicitante == destinatario:
        messages.warning(request, "No puedes solicitar intercambio para tu propio libro.")
        return redirect('home')

    # Condición 2: Verificar si ya existe una solicitud pendiente de este usuario para este libro
    solicitud_existente = Solicitudintercambio.objects.filter(
        solicitante=solicitante,
        destinatario=destinatario,
        libro=libro,
        estado='pendiente'
    ).first()

    if solicitud_existente:
        messages.info(request, "Ya has enviado una solicitud de intercambio para este libro.")
        return redirect('home')

    # Crear nueva solicitud de intercambio
    try:
        solicitud = Solicitudintercambio.objects.create(
            solicitante=solicitante,
            destinatario=destinatario,
            libro=libro,
            estado='pendiente'
        )
        messages.success(request, "Solicitud de intercambio creada correctamente.")
    except Exception as e:
        print(f"Error al crear la solicitud: {e}")
        messages.error(request, "Error al crear la solicitud de intercambio.")
    return redirect('home')



from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Solicitudintercambio, LVentaU, AuthUser

@login_required
def solicitar_intercambio(request):
    try:
        # Obtener los parámetros de la URL
        libro_id_objetivo = request.GET.get('libro_id_objetivo')
        libro_intercambio_id = request.GET.get('libro_intercambio')

        # Mensajes de depuración para confirmar que los valores son correctos
        print("Libro objetivo ID:", libro_id_objetivo)
        print("Libro intercambio ID:", libro_intercambio_id)

        if libro_id_objetivo and libro_intercambio_id:
            # Obtener los objetos correspondientes
            libro_objetivo = get_object_or_404(LVentaU, id=libro_id_objetivo)
            libro_intercambio = get_object_or_404(LVentaU, id=libro_intercambio_id, usuario=request.user.id)

            solicitante = AuthUser.objects.get(id=request.user.id)
            destinatario = libro_objetivo.usuario

            # Verificar que el solicitante no sea el propietario del libro
            if solicitante == destinatario:
                messages.warning(request, "No puedes solicitar intercambio para tu propio libro.")
                return redirect('home')

            # Verificar si ya existe una solicitud pendiente
            solicitud_existente = Solicitudintercambio.objects.filter(
                solicitante=solicitante,
                destinatario=destinatario,
                libro=libro_objetivo,
                estado='pendiente'
            ).first()

            if solicitud_existente:
                messages.info(request, "Ya has enviado una solicitud de intercambio para este libro.")
                return redirect('home')

            # Crear nueva solicitud de intercambio
            try:
                Solicitudintercambio.objects.create(
                    solicitante=solicitante,
                    destinatario=destinatario,
                    libro=libro_objetivo,
                    libro_intercambio=libro_intercambio,  # Asignar el libro seleccionado por el usuario
                    estado='pendiente'
                )
                messages.success(request, "Solicitud de intercambio creada correctamente.")
            except Exception as e:
                print(f"Error al crear la solicitud: {e}")
                messages.error(request, "Error al crear la solicitud de intercambio.")
        else:
            messages.error(request, "No se recibieron los parámetros necesarios para el intercambio.")

    except Exception as e:
        print(f"Error en la vista de solicitar_intercambio: {e}")
        messages.error(request, "Ocurrió un problema inesperado al procesar la solicitud de intercambio.")

    return redirect('home')





from django.utils import timezone  # Asegúrate de tener esto importado

def libro_detalle(request, libro_id):
    libro = Libro.objects.get(id=libro_id)
    comentarios = Comentarios.objects.filter(libro=libro).order_by('-fecha')
    user = request.user
    user = user.id
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comentario_texto = request.POST.get('comment')
        usuario = AuthUser.objects.get(id=user)

        # Crear un nuevo comentario solo si el usuario está autenticado
        if request.user.is_authenticated:
            nuevo_comentario = Comentarios.objects.create(
                libro=libro,
                usuario=usuario,
                calificacion=rating,
                comentario=comentario_texto,
                fecha=timezone.now()  # Aquí está el campo correcto
            )
            nuevo_comentario.save()

            return redirect('libro_detalle', libro_id=libro_id)

    data = {
        'libro': libro,
        'comentarios': comentarios
    }
    return render(request, 'app/libro_detalle.html', data)













@login_required
def mesa_ayuda_usuario(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        user = request.user
        user = user.id
        usuario = AuthUser.objects.get(id=user)

        problema = Problema.objects.create(
            usuario=usuario, 
            descripcion=descripcion,
            estado='abierto',
            fecha_creacion=timezone.now()
            )
        problema.save()
        messages.success(request, "Problema reportado exitosamente.")
        return redirect('mesa_ayuda_usuario')
    
    problemas = Problema.objects.filter(usuario=request.user.id).order_by('-fecha_creacion')
    
    return render(request, 'app/mesa_ayuda_usuario.html', {'problemas': problemas})



@login_required
def mesa_ayuda_trabajador(request):
    if not request.user.is_staff:
        return redirect('home')  # Solo trabajadores tienen acceso
    
    problemas = Problema.objects.filter(estado='abierto').order_by('-fecha_creacion')
    
    if request.method == 'POST':
        problema_id = request.POST.get('problema_id')
        respuesta_texto = request.POST.get('respuesta')
        problema = get_object_or_404(Problema, id=problema_id)
        Respuesta.objects.create(problema=problema, respuesta=respuesta_texto, respondido_por=request.user.id)
        problema.estado = 'cerrado'
        problema.save()
        messages.success(request, "Respuesta enviada y problema cerrado.")
        return redirect('mesa_ayuda_trabajador')

    return render(request, 'app/mesa_ayuda_trabajador.html', {'problemas': problemas})


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Problema, Respuesta
from django.contrib import messages

@login_required
def mesa_ayuda_trabajador(request):
    if not request.user.is_staff:  # Solo trabajadores (staff) pueden acceder
        return redirect('home')
    
    # Obtener problemas abiertos
    problemas = Problema.objects.filter(estado='abierto').order_by('-fecha_creacion')

    if request.method == 'POST':
        problema_id = request.POST.get('problema_id')
        respuesta_texto = request.POST.get('respuesta')
        problema = get_object_or_404(Problema, id=problema_id)

        Respuesta.objects.create(
            problema=problema,
            respuesta=respuesta_texto,
            respondido_por=request.user
        )
        problema.estado = 'cerrado'
        problema.save()

        messages.success(request, 'El problema ha sido resuelto correctamente.')
        return redirect('mesa_ayuda_trabajador')

    return render(request, 'app/mesa_ayuda_trabajador.html', {'problemas': problemas})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Problema
from django.contrib import messages

@login_required
def crear_ticket(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        user = request.user
        user = user.id
        usuario = AuthUser.objects.get(id=user)
        
        if descripcion:
            Problema.objects.create(
                usuario=usuario,
                descripcion=descripcion,
                estado='abierto',
                fecha_creacion = timezone.now()
            )
            messages.success(request, 'Tu solicitud ha sido enviada. Te contactaremos pronto.')
            return redirect('mesa_ayuda_usuario')
        else:
            messages.error(request, 'Por favor describe el problema.')
    
    return render(request, 'app/crear_ticket.html')


# views.py
from django.shortcuts import render, get_object_or_404
from .models import AuthUser, Usuarios  # Ajusta según el nombre de tu modelo de usuario

def biografia_usuario(request, user_id):
    usuario = get_object_or_404(AuthUser, id=user_id)
    usu = get_object_or_404(Usuarios, id=user_id)  # O como esté relacionado en tu modelo
    data = {
        'usuario': usuario,
        'usu': usu
    }
    return render(request, 'app/biografia_usuario.html', data)

def autor_detalle(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)
    libros = Libro.objects.filter(autor=autor_id)  # Asumiendo que hay una relación de 'libro' con 'autor'
    context = {
        'autor': autor,
        'libros': libros
    }
    return render(request, 'app/autor_detalle.html', context)
















def administrador(request):
    return render(request, 'app/administrador.html', {
    })
def reportes(request):
    return render(request, 'app/reportes.html', {
    })

def confirmacion_pago(request):
    return render(request, 'app/confirmacion_pago.html', {
    })


def recuperar_contraseña(request):
    return render(request, 'app/recuperar_contraseña.html', {
    })



