from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Diccionario para simular el progreso de cada usuario (tema desbloqueado más alto)
# En producción deberías usar un modelo en la base de datos en lugar de este dict en memoria.
progreso = {}

def index(request):
    """
    Vista principal:
    - Si es POST: procesa login.
    - Si GET y usuario autenticado: muestra menu de temas (index.html) pasando 'progreso'.
    - Si GET y no autenticado: muestra login.
    """
    # --- Login (POST) ---
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # inicializa progreso si no existe
            if username not in progreso:
                progreso[username] = 1
            # después de iniciar sesión vamos al índice (menu de temas)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

    # --- GET ---
    if request.user.is_authenticated:
        # asegúrate de que el usuario tiene entrada en el dict para evitar KeyError en la plantilla
        progreso.setdefault(request.user.username, 1)
        # renderiza index.html y pasa el dict 'progreso' (la plantilla usa el filtro get_item)
        return render(request, 'index.html', {'progreso': progreso})
    else:
        return render(request, 'login.html')


def registro(request):
    """
    Vista para registrar un nuevo usuario.
    """
    from django.contrib.auth.models import User
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password1')


        if not username or not password:
            return render(request, 'registro.html', {'error': 'Completa todos los campos'})

        if User.objects.filter(username=username).exists():
            return render(request, 'registro.html', {'error': 'El usuario ya existe'})

        User.objects.create_user(username=username, password=password)
        # inicializa progreso para el nuevo usuario
        progreso[username] = 1
        return redirect('login')

    return render(request, 'registro.html')


def logout_view(request):
    """
    Cierra la sesión y redirige al login.
    """
    logout(request)
    return redirect('login')


@login_required
def aprendizaje(request, tema):
    """
    Controla el acceso a los temas de aprendizaje.
    Solo se puede acceder si el usuario ha desbloqueado el tema anterior.
    """
    user = request.user.username
    tema_actual = progreso.get(user, 1)

    if tema > tema_actual:
        # Tema bloqueado
        return render(request, "bloqueado.html", {"tema": tema})
    return render(request, f"aprendizaje{tema}.html")


@login_required
def completar_tema(request, tema):
    """
    Cuando el usuario completa un tema, se desbloquea el siguiente.
    La vista espera que el formulario de preguntas haga POST a esta URL o que el usuario
    haga click en un enlace que vaya a /completar/<tema>/ (según tu implementación).
    """
    user = request.user.username
    tema_actual = progreso.get(user, 1)

    # Si el usuario completa el tema que corresponde a su progreso, desbloquea el siguiente
    if tema >= tema_actual:
        progreso[user] = tema + 1  # desbloquea el siguiente tema

    siguiente_tema = tema + 1
    # si no tienes más temas, redirige al índice (ajusta el número máximo si añades más temas)
    MAX_TEMAS = 10  # pon aquí el número de temas que tendrás (por ahora 2 está bien)
    if siguiente_tema > MAX_TEMAS:
        return redirect('index')

    return redirect('aprendizaje', tema=siguiente_tema)


@login_required
def juego1(request):
    return render(request, 'juego1.html')


@login_required
def preguntas1(request):
    return render(request, 'preguntas1.html')


@login_required
def juego2(request):
    return render(request, 'juego2.html')


@login_required
def preguntas2(request):
    return render(request, 'preguntas2.html')
