# %%
!pip install agentpy  owlready2
!pip install matplotlib

# %%
import agentpy as ap
from matplotlib import pyplot as plt
import IPython
import random
from owlready2 import *
#from flask import Flask

# %%
onto = get_ontology("file://onto.owl")
#app = Flask(__name__)
#@app.route('/')
#def index():
#    return "Hello World"

# %%
#ONTOLOGIA
with onto:

    class Entity(Thing):
        pass

    class Robot(Entity):
        pass
    
    class Box(Entity):
        pass
    
    class Obstacle(Entity):
        pass

    class Place(Thing):
        pass

    class Position(Thing):
        pass

    class has_place(ObjectProperty, FunctionalProperty):
        domain = [Entity]
        range = [Place]

    class has_position(DataProperty, FunctionalProperty):
        domain = [Place]
        range = [str]
        pass
    
    
        

# %%
class RobotAgent(ap.Agent):
    
    #RAZONAMIENTO DEL AGENTE---------------------------------------------------
    def see(self,e):
        """
        Función de percepción
        @param e: entorno grid
        """
        self.per = []
        vecinos = e.neighbors(self,1)
        # Creación de percepto: lista de creencias de agentes Dirt
        for vecino in vecinos:
            self.per.append(Box(has_place=Place(has_position=str(e.positions[vecino]))))
        pass

    def next(self):
        """
        Función de razonamiento Deductivo
        """
        # Por cada acción
        for act in self.actions:
            # Por cada regla
            for rule in self.rules:
                # Si la acción es válidad dada la regla
                if rule(act):
                    # Ejecuta la acción
                    act()
        pass

# REGLAS-------------------------------------------------------------------
    def rule_1(self, act):
        """
        Regla deductiva para recoger la caja
        @param act: acción a validar
        @return: booleano
        """
        # Validador de regla
        validador = [False, False]

        # Proposición 1: Si hay cajas en la posición actual
        for box in self.model.boxes:
            if box.pos == self.model.grid.positions[self]:
                validador[0] = True

        # Proposición 2: Si la acción es la de recoger
        if act == self.pickup:
            validador[1] = True

        return all(validador)

    def rule_2(self, act):
        validador = [False, False, False]

        for box in self.per:
            if eval(box.has_place.has_position)[0] == self.model.grid.positions[self][0] - 1:
                validador[0] = True

        if act == self.move_N:
            validador[1] = True

        if self.model.grid.positions[self][0] - 1 >= 0:
            agents_at_pos = [
                agent for agent in self.model.grid.agents
                if self.model.grid.positions[agent] == (self.model.grid.positions[self][0] - 1, self.model.grid.positions[self][1])
            ]
            if not any(isinstance(agent, RobotAgent) for agent in agents_at_pos):
                validador[2] = True

        return all(validador)

    def rule_3(self, act):
        validador = [False, False, False]

        for box in self.per:
            if eval(box.has_place.has_position)[0] == self.model.grid.positions[self][0] + 1:
                validador[0] = True

        if act == self.move_S:
            validador[1] = True

        if self.model.grid.positions[self][0] + 1 < self.model.grid.shape[0]:
            agents_at_pos = [
                agent for agent in self.model.grid.agents
                if self.model.grid.positions[agent] == (self.model.grid.positions[self][0] + 1, self.model.grid.positions[self][1])
            ]
            if not any(isinstance(agent, RobotAgent) for agent in agents_at_pos):
                validador[2] = True

        return all(validador)

    def rule_4(self, act):
        validador = [False, False, False]

        for box in self.per:
            if eval(box.has_place.has_position)[1] == self.model.grid.positions[self][1] + 1:
                validador[0] = True

        if act == self.move_E:
            validador[1] = True

        if self.model.grid.positions[self][1] + 1 < self.model.grid.shape[1]:
            agents_at_pos = [
                agent for agent in self.model.grid.agents
                if self.model.grid.positions[agent] == (self.model.grid.positions[self][0], self.model.grid.positions[self][1] + 1)
            ]
            if not any(isinstance(agent, RobotAgent) for agent in agents_at_pos):
                validador[2] = True

        return all(validador)

    def rule_5(self, act):
        validador = [False, False, False]

        for box in self.per:
            if eval(box.has_place.has_position)[1] == self.model.grid.positions[self][1] - 1:
                validador[0] = True

        if act == self.move_W:
            validador[1] = True

        if self.model.grid.positions[self][1] - 1 >= 0:
            agents_at_pos = [
                agent for agent in self.model.grid.agents
                if self.model.grid.positions[agent] == (self.model.grid.positions[self][0], self.model.grid.positions[self][1] - 1)
            ]
            if not any(isinstance(agent, RobotAgent) for agent in agents_at_pos):
                validador[2] = True

        return all(validador)

    def rule_6(self, act):
        """
        Regla deductiva para moverse aleatoriamente
        @param act: acción a validar
        @return: booleano
        """

        # Validador de regla
        validador = [False, False]

        # Proposición 1: Si no hay cajas en el entorno
        if len(self.per) == 0:
            validador[0] = True

        # Proposición 2: Si la acción es la de moverse aleatoriamente
        if act == self.move_random:
            validador[1] = True

        return all(validador)

    def rule_separate(self, act):
        """
        Regla para alejarse si hay otro robot adyacente.
        @param act: acción a validar
        @return: booleano
        """
        validador = [False, False]

        # Proposición 1: Si hay otro robot en una posición adyacente
        vecinos = self.model.grid.neighbors(self, 1)
        if any(isinstance(vecino, RobotAgent) for vecino in vecinos):
            validador[0] = True

        # Proposición 2: Si la acción es moverse lejos
        if act == self.move_away:
            validador[1] = True

        return sum(validador) == 2



    
    #SIMULACION DEL AGENTE-----------------------------------------------------
    def setup(self):
        self.agentType = 0 # Tipo de agente
        self.carrying = None
        #self.moves = 0
        self.direction = (-1, 0) 
        self.pos = None

        # Acciones del agente
        self.actions = (
            self.pickup,
            self.move_N,
            self.move_S,
            self.move_E,
            self.move_W,
            self.move_random,
            self.move_away  # Nueva acción añadida aquí
        )

        self.rules = (
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
            self.rule_6,
            self.rule_separate  # Nueva regla añadida aquí
        )

        pass
    
    def step(self):
        self.see(self.model.grid)
        self.next()
        
    
        #ACCIONES
    def move_N(self):
        """
        Función de movimiento hacia el norte
        """
        self.direction = (-1,0) #Cambio de dirección
        self.forward() # Caminar un paso hacia adelante

    def move_S(self):
        """
        Función de movimiento hacia el sur
        """
        self.direction = (1,0) #Cambio de dirección
        self.forward() # Caminar un paso hacia adelante

    def move_E(self):
        """
        Función de movimiento hacia el este
        """
        self.direction = (0,1) #Cambio de dirección
        self.forward() # Caminar un paso hacia adelante

    def move_W(self):
        """
        Función de movimiento hacia el oeste
        """
        self.direction = (0,-1) #Cambio de dirección
        self.forward() # Caminar un paso hacia adelante

    def move_random(self):
        """
        Función de movimiento aleatorio
        """
        # Rotaciones aleatorias
        for _ in range(random.randint(0,4)):
            self.turn()
        self.forward() # Caminar un paso hacia adelante

    def pickup(self):
        """
        Función de limpieza
        """
        #Si hay suciedad en la posición actual
        for box in self.model.grid.agents:
          if box.agentType == 1:
            if box.pos == self.model.grid.positions[self]:
              self.model.grid.remove_agents(box) #Recoger la caja
              break #Romper ciclo
        pass

    def forward(self):
        """
        Función de movimiento
        """
        self.model.grid.move_by(self, self.direction)
        pass

    def turn(self):
        """
        Función de rotación
        """
        if self.direction == (-1,0):
            self.direction = (0,1) #Hacia Este
        elif self.direction == (0,1):
            self.direction = (1,0)  #Hacia Sur
        elif self.direction == (1,0):
            self.direction = (0,-1) #Hacia Oeste
        elif self.direction == (0,-1):
            self.direction = (-1,0) #Hacia Norte
        pass
    
    def move_away(self):
        """
        Función para alejarse si hay otro robot adyacente.
        """
        # Encuentra posiciones adyacentes disponibles
        possible_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(possible_directions)
        
        for direction in possible_directions:
            new_position = (self.model.grid.positions[self][0] + direction[0], 
                            self.model.grid.positions[self][1] + direction[1])
            
            if (0 <= new_position[0] < self.model.grid.shape[0] and 
                0 <= new_position[1] < self.model.grid.shape[1]):
                
                agents_at_new_pos = [
                    agent for agent in self.model.grid.agents
                    if self.model.grid.positions[agent] == new_position
                ]
                if not any(isinstance(agent, RobotAgent) for agent in agents_at_new_pos):
                    self.direction = direction
                    self.forward()
                    break


# %%


# %%
class BoxAgent(ap.Agent):
    def setup(self):
        self.agentType = 1
        self.first_step = True
        self.pos = None
        pass

    def step(self):
        if self.first_step:
          self.pos = self.model.grid.positions[self]
          self.first_step = False
        pass

# %%
class RobotModel(ap.Model):
    """
    Función de inicialización
    """
    def setup(self):
        # Instancias lista de agentes robots
        self.robots = ap.AgentList(self, self.p.robots, RobotAgent)
        # Instancias lista de agentes cajas
        self.boxes = ap.AgentList(self, self.p.boxes, BoxAgent)

        # Instancia grid
        self.grid = ap.Grid(self, (self.p.M, self.p.N), track_empty=True)

        # Asignación de agentes a grid
        self.grid.add_agents(self.robots, random=True, empty=True)
        self.grid.add_agents(self.boxes, random=True, empty=True)
        pass

    def step(self):
        """
        Función paso a paso
        """
        self.robots.step() #Paso de robot
        self.boxes.step() #Paso de caja
        pass
    
    def update(self):
        pass
    
    def end(self):
        pass

# %%


# %%


# %%
parameters = {
    'M': 10,
    'N': 10,
    "steps": 100,
    'robots': 4,
    'boxes': 10
}

#model = RobotModel(parameters)
#results = model.run()

# %%
#A FUNCTION TO ANIMATE THEE SIMULATION

def animation_plot(model, ax):
    """
    Función de animación
    @param model: modelo
    @param ax: axes (matplotlib)
    """
    # Definición de atributo para tipo de agente
    agent_type_grid = model.grid.attr_grid('agentType')
    # Definición de gráfico con colores (de acuerdo al tipo de agente)
    ap.gridplot(agent_type_grid, cmap='Accent', ax=ax)
    # Definición de título del gráfico
    ax.set_title(f"Robot Model \n Time-step: {model.t}, "
                 f"Boxes: {0}")

# %%
#SIMULATION:

#Create figure (from matplotlib)
fig, ax = plt.subplots()

#Create model
model = RobotModel(parameters)

#Run with animation
#If you want to run it without animation then use instead:
#model.run()
animation = ap.animate(model, fig, ax, animation_plot)
#This step may take a while before you can see anything

#Print the final animation
IPython.display.HTML(animation.to_jshtml())


