from openai import OpenAI
client = OpenAI()

''' 
audio_file= open("test_audio.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)

'''

system_prompt = '''Eres un transcriptor de datos a estructuras ordenadas. Debes identificar el ejercicio, el numero de la serie, las repeticiones y los kilos. Debes devolver los datos como json con keys exercise, repetition, series, kg and rir. Rir se refiere a las repeticiones del fallo que se ha quedado. Si falta algun campo debes poner ERROR. El nombre del ejercicio tiene que ser de esta lista, si no hay un match exacto debe ser el más parecido - Fondos Asistidos
- Press de Banca con Banda Elástica
- Fondos en Barra
- Press de Banca
- Press de Banca Contra Banda
- Press de Banca con Tablas
- Press de Pecho en Polea
- Press de Banca Agarre Cerrado
- Press de Banca Agarre Cerrado con Pies Elevados
- Press de Banca Declinado
- Flexiones Declinadas
- Aperturas con Mancuernas
- Press de Pecho con Mancuernas
- Press Declinado con Mancuernas
- Press de Suelo con Mancuernas
- Pullover con Mancuernas
- Press de Banca con Pies Elevados
- Press de Suelo
- Press de Banca Inclinado
- Press Inclinado con Mancuernas
- Flexiones Inclinadas
- Press de Suelo con Pesa Rusa
- Flexiones Inclinadas de Rodillas
- Flexiones de Rodillas
- Aperturas en Máquina
- Press de Pecho en Máquina
- Máquina Pec Deck
- Press de Banca con Pines
- Flexiones
- Flexiones Contra la Pared
- Flexiones con Pies en Anillas
- Aperturas con Banda Elástica
- Fondos en Anillas
- Press de Banca en Máquina Smith
- Press de Banca Inclinado en Máquina Smith
- Press de Banca Agarre Inverso en Máquina Smith
- Aperturas de Pie en Polea
- Aperturas de Pie con Banda Elástica


- Press Arnold
- Rotación Externa con Banda
- Rotación Interna con Banda
- Aperturas con Banda
- Elevaciones Frontales con Barra
- Remo para Deltoides Posterior con Barra
- Remo Vertical con Barra
- Press Tras Nuca
- Elevaciones Laterales en Polea
- Remo para Deltoides Posterior en Polea
- Press Cubano
- Elevaciones Frontales con Mancuernas
- Rotación Interna Horizontal con Mancuernas
- Rotación Externa Horizontal con Mancuernas
- Elevaciones Laterales con Mancuernas
- Remo para Deltoides Posterior con Mancuernas
- Press de Hombros con Mancuernas
- Face Pull
- Elevación Frontal Isométrica
- Press Landmine
- Rotación Externa Tumbado con Mancuernas
- Rotación Interna Tumbado con Mancuernas
- Elevaciones Laterales en Máquina
- Press de Hombros en Máquina
- Remo Monkey
- Press Militar
- Elevaciones Frontales con Disco
- Jerk de Potencia
- Push Press
- Aperturas Inversas en Polea
- Aperturas Inversas con Mancuernas
- Aperturas Inversas en Máquina
- Press de Hombros Sentado con Mancuernas
- Press Militar Sentado
- Press de Hombros Sentado en Máquina Smith
- Press Tras Nuca Agarre de Snatch
- Jerk en Squat
- Split Jerk


- Curl con Barra
- Curl Predicador con Barra
- Curl Bayesiano
- Curl con Peso Corporal
- Curl de Bíceps en Polea Cruzada
- Curl en Polea con Barra
- Curl en Polea con Cuerda
- Curl de Concentración
- Curl Arrastrado
- Curl con Mancuernas
- Curl Predicador con Mancuernas
- Curl Martillo
- Curl Inclinado con Mancuernas
- Curl de Bíceps en Máquina
- Curl Spider


- Extensión de Tríceps de Pie con Barra
- Extensión de Tríceps Tumbado con Barra
- Fondos en Banco
- Extensión de Tríceps en Polea Cruzada
- Flexiones Agarre Cerrado
- Extensión de Tríceps Tumbado con Mancuernas
- Extensión de Tríceps de Pie con Mancuernas
- Extensión de Tríceps en Polea Alta
- Extensión de Tríceps con Peso Corporal
- Press de Tríceps en Polea con Barra
- Press de Tríceps en Polea con Cuerda

- Sentadilla sin Peso
- Sentadilla Hack con Barra
- Zancada con Barra
- Zancada Caminando con Barra
- Sentadilla con Cinturón
- Zancada sin Peso
- Curl de Piernas con Peso Corporal
- Salto a Cajón
- Sentadilla a Cajón
- Sentadilla Búlgara
- Sentadilla en Silla
- Zancada con Mancuernas
- Sentadilla con Mancuernas
- Sentadilla Frontal
- Sentadilla Goblet
- Máquina Hack
- Media Sentadilla sin Peso
- Máquina de Aducción
- Zancada con Salto
- Sentadilla Hack Landmine
- Sentadilla Landmine
- Curl de Piernas con Pelota
- Extensión de Piernas
- Prensa de Piernas
- Curl de Piernas Tumbado
- Curl Nórdico Excéntrico
- Sentadilla con Pausa
- Zancada Inversa con Barra
- Peso Muerto Rumano
- Sentadilla con Barra de Seguridad
- Curl de Piernas Sentado
- Zancada Superficial sin Peso
- Zancadas Laterales (sin Peso)
- Sentadilla Búlgara en Máquina Smith
- Sentadilla en Máquina Smith
- Sentadilla
- Subida a Step
- Sentadilla Zercher
- Sentadilla Zombie

- Dominada Asistida
- Pull-Up Asistida
- Extensión de Espalda
- Muscle-Up con Banda
- Remo con Barra
- Encogimientos con Barra
- Clean desde Bloques
- Snatch desde Bloques
- Remo Sentado Agarre Cerrado en Polea
- Remo Sentado Agarre Ancho en Polea
- Pecho a Barra
- Dominada Supina
- Clean
- Clean and Jerk
- Peso Muerto
- Peso Muerto con Déficit
- Peso Muerto con Mancuernas
- Remo con Mancuerna
- Encogimientos con Mancuernas
- Extensión de Espalda en Suelo
- Good Morning
- Remo Gorilla
- Hang Clean
- Hang Power Clean
- Hang Power Snatch
- Hang Snatch
- Remo Invertido
- Remo Invertido Agarre Supino
- Curl Jefferson
- Muscle-Up con Salto
- Swing con Pesa Rusa
- Jalón al Pecho Agarre Prono
- Jalón al Pecho Agarre Supino
- Muscle-Up (Barra)
- Muscle-Up (Anillas)
- Remo Unilateral en Polea
- Jalón Unilateral
- Peso Muerto con Pausa
- Remo Pendlay
- Power Clean
- Power Snatch
- Pull-Up
- Pull-Up Agarre Neutro
- Rack Pull
- Pull-Up en Anillas
- Remo en Anillas
- Scap Pull-Up
- Remo Seal
- Remo en Máquina Sentado
- Peso Muerto a Una Pierna con Pesa Rusa
- Snatch
- Peso Muerto Agarre Snatch
- Peso Muerto Piernas Rígidas
- Jalón Recto
- Peso Muerto Sumo
- Remo en T
- Peso Muerto con Barra Hexagonal Agarres Altos
- Peso Muerto con Barra Hexagonal Agarres Bajos

- Patadas Laterales con Banda
- Pull Through en Polea
- Aberturas de Cadera
- Sentadilla Cossack
- Marcha de la Muerte con Mancuernas
- Patadas de Burro
- Peso Muerto Rumano con Mancuernas
- Hip Thrust Rana con Mancuernas
- Patadas de Bombero
- Hip Thrust Rana
- Puente de Glúteos
- Abducción de Cadera con Banda
- Máquina de Abducción de Cadera
- Hip Thrust
- Máquina de Hip Thrust
- Hip Thrust con Banda en Rodillas
- Caminata Lateral con Banda
- Patadas de Glúteos en Máquina
- Puente de Glúteos a Una Pierna
- Hip Thrust a Una Pierna
- Hiperextensión Inversa
- Peso Muerto Rumano
- Peso Muerto Rumano a Una Pierna
- Patada de Glúteos de Pie en Máquina
- Subida a Step


- Lanzamientos de Balón
- Crunch en Polea
- Crunch
- Dead Bug
- Dragon Flag
- Elevación de Rodillas Colgado
- Elevación de Piernas Colgado
- Sit-Up Colgado
- Limpiaparabrisas Colgado
- Wood Chop Alto a Bajo con Banda
- Wood Chop Horizontal con Banda
- Rueda Abdominal de Rodillas
- Plancha de Rodillas
- Plancha Lateral de Rodillas
- Elevación de Piernas Tumbado
- Limpiaparabrisas Tumbado
- Limpiaparabrisas Tumbado con Rodillas Flexionadas
- Crunch en Máquina
- Mountain Climbers
- Crunch Oblicuo
- Sit-Up Oblicuo
- Plancha
- Plancha con Elevación de Piernas
- Giro Ruso
- Plancha Lateral
- Sit-Up


- Elevación de Talones de Pie con Barra
- Elevación de Talones Burro
- Bajada de Talón Excéntrica
- Elevación de Talón
- Elevación de Talones Sentado
- Elevación de Talones de Pie

- Curl de Muñeca con Barra
- Curl de Muñeca con Barra por Detrás
- Cuelgue en Barra
- Curl de Muñeca con Mancuerna
- Caminata del Granjero
- Peso Muerto con Barra Gruesa
- Gripper
- Cuelgue en Barra a Una Mano
- Pinza con Disco
- Curl de Muñeca con Disco
- Dominada con Toalla
- Rodillo de Muñeca


- Extensión de Muñeca con Barra
- Extensión de Muñeca con Mancuerna

'''
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "tercera serie con 200 kg 8 repeticiones de Press banca"
            }
        ]
)

print(completion.choices[0].message.content)