#.....................................................................................
# Código de prueba utilizando flask, 2025.
# hecho por FECORO.
# | Esta es una aplicación que genera un juego básico utilizando python y html |
#.....................................................................................

#.......................................... || STACK:
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os

#......................................... ||  CODE
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # ..genera una clave secreta aleatoria
# ..definición del mapa del juego: cada habitación tiene una descripción, conexiones y objetos.
rooms = {
    "Vestíbulo": {
        "description": "Estás en el vestíbulo de la mansión. Hay puertas al norte y al este.",
        "exits": {"norte": "Biblioteca", "este": "Cocina"},
        "items": ["linterna"]
    },
    "Biblioteca": {
        "description": "La biblioteca está llena de libros antiguos y secretos. Solo ves una salida al sur.",
        "exits": {"sur": "Vestíbulo"},
        "items": ["llave antigua"]
    },
    "Cocina": {
        "description": "La cocina desprende aromas extraños. Hay una puerta al oeste y unas escaleras que bajan al sótano.",
        "exits": {"oeste": "Vestíbulo", "abajo": "Sótano"},
        "items": []
    },
    "Sótano": {
        "description": "El sótano es oscuro y tétrico, con un ambiente misterioso. La única salida es subiendo de nuevo a la cocina.",
        "exits": {"arriba": "Cocina"},
        "items": ["caja fuerte"]
    }
}

# ..formulario para ingresar comandos (por ejemplo: "mover norte", "tomar linterna", "inventario")
class CommandForm(FlaskForm):
    command = StringField('Ingresa un comando', validators=[DataRequired()])
    submit = SubmitField('Ejecutar')



#......................................... FUNC:
def init_game():
    """
    Inicializa la sesión del juego con estado inicial.
    """
    session['current_room'] = "Vestíbulo"
    session['inventory'] = []
    session['log'] = ["¡Bienvenido a la Mansión Misteriosa! Comienza tu aventura en el vestíbulo."]

def process_command(command):
    """
    Procesa el comando ingresado por el jugador.
    Los comandos pueden ser:
     - mover <dirección>
     - tomar <objeto>
     - inventario
    """
    command = command.lower().strip()
    tokens = command.split()
    if not tokens:
        return "No has ingresado ningún comando."

    verb = tokens[0]

    # ..comando: mover <dirección>
    if verb == "mover" and len(tokens) >= 2:
        direction = tokens[1]
        current_room = session.get('current_room')
        room_data = rooms.get(current_room)
        if direction in room_data["exits"]:
            new_room = room_data["exits"][direction]
            session['current_room'] = new_room
            message = f"Te has movido a la habitación: {new_room}."
            session['log'].append(message)
            return message
        else:
            message = "No puedes moverte en esa dirección desde aquí."
            session['log'].append(message)
            return message

    # ..comando: tomar <objeto>
    elif verb == "tomar" and len(tokens) >= 2:
        item = " ".join(tokens[1:])
        current_room = session.get('current_room')
        room_data = rooms.get(current_room)
        if item in room_data["items"]:
            # ..agrega el objeto al inventario y se quita de la habitación
            inventory = session.get('inventory')
            inventory.append(item)
            session['inventory'] = inventory
            room_data["items"].remove(item)
            message = f"Has tomado el objeto: {item}."
            session['log'].append(message)
            return message
        else:
            message = f"El objeto '{item}' no se encuentra en esta habitación."
            session['log'].append(message)
            return message

    # Comando: inventario
    elif verb == "inventario":
        inventory = session.get('inventory')
        if inventory:
            message = "Tu inventario contiene: " + ", ".join(inventory)
        else:
            message = "Tu inventario está vacío."
        session['log'].append(message)
        return message

    # ..comando desconocido
    else:
        message = "Comando no reconocido. Prueba 'mover <dirección>', 'tomar <objeto>' o 'inventario'."
        session['log'].append(message)
        return message

@app.route('/', methods=['GET', 'POST'])
def game():
    # ..si no hay estado en la sesión, inicializar el juego.
    if 'current_room' not in session:
        init_game()

    form = CommandForm()
    output_message = None

    if form.validate_on_submit():
        user_command = form.command.data
        output_message = process_command(user_command)
        form.command.data = ""  # ..limpia el apartado de texto
        # ..redirige para evitar reenvío de formulario
        return redirect(url_for('game'))

    # ..recolecta datos actuales del juego
    current_room = session.get('current_room')
    room_data = rooms.get(current_room)
    inventory = session.get('inventory')
    log = session.get('log')

    return render_template('game.html',
                           current_room=current_room,
                           room_description=room_data["description"],
                           exits=room_data["exits"],
                           items=room_data["items"],
                           inventory=inventory,
                           log=log,
                           form=form)

@app.route('/reiniciar')
def reiniciar():
    """
    Ruta para reiniciar el juego.
    """
    session.clear()
    flash("El juego se ha reiniciado.", "info")
    return redirect(url_for('game'))

if __name__ == '__main__':
    app.run(debug=True)
