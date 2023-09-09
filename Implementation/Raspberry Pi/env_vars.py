'''
    The next variables can be changed since they are relative to limits or text
'''

"""
    In this file are defined the system variables
"""

#Temperature variables
temperature_max = 30
temperature_min = 22
temperature_min_text   = "Está um pouco frio. Considere aumentar a Temperatura ambiente"
temperature_ideal_text = "A Temperatura está ideal!"
temperature_max_text   = "Está calor. Considere reduzir a Temperatura ambiente" 
temperature_description= "Uma das coisas mais importantes que um produtor pode fazer é manter uma temperatura \
                         uniforme e consistente. Uma temperatura uniforme significa que a temperatura da sala de \
                         cultivo é a mesma em todas as áreas, de uma extremidade à outra."
temperature_max_warning_text = "Atenção: Elevada temperatura ambiente!"
temperature_min_warning_text = "Atenção: Baixa temperatura ambiente!"


#Water Temperature variables
water_temperature_max = 24
water_temperature_min = 18.3
water_temperature_min_text   = "Está um pouco frio. Considere aumentar a Temperatura da Água"
water_temperature_ideal_text = "A Temperatura da água está ideal!"
water_temperature_max_text   = "Está calor. Considere reduzir a Temperatura da Água" 
water_temperature_description= " E é importante manter a solução sempre com protegido da luz, para evitar o \
                               desenvolvimento de algas. Nas regiões de muito calor, os cultivos absorvem uma \
                               quantidade maior de água do que nutrientes e é necessário trabalhar com soluções \
                               mais diluídas. "
water_temperature_max_warning_text = "Atenção: Elevada temperatura na solução!"
water_temperature_min_warning_text = "Atenção: Baixa temperatura na solução!"


#Humidity variables
humidity_max = 70
humidity_min = 40
humidity_min_text   = "O ambiente está seco. Considere aumentar a Humidade do ambiente"
humidity_ideal_text = "A Humidade do ambiente está ideal!"
humidity_max_text   = "O ambiente está bastante humido. Considere reduzir a Humidade do ambiente"
humidity_description= "Uma humidade adequada é importante para a absorção de nutrientes e o crescimento saudável das plantas.\
                      Uma humidade muito baixa ou muito alta pode prejudicar o crescimento das plantas."
humidity_max_warning_text = "Atenção: Elevada humidade ambiente!"
humidity_min_warning_text = "Atenção: Baixa humidade ambiente!"


#pH variables
ph_max = 6.5
ph_min = 5.2
ph_min_text   = "A solução está demasiado ácida. Considere aumentar o pH"
ph_ideal_text = "O pH da solução está ideal!"
ph_max_text   = "A solução está demasiado alcalina/básica. Considere diminuir o pH"
ph_description= "O pH mede a acidez relativa ou alcalinidade/basicidade de uma solução. \
                Na hidroponia determina-se o nível de pH da água antes de se adicionarem nutrientes. \n \
                É medido numa escala de 1 a 14, sendo o ponto considerado neutro 7. \
                Acima de 7 é considerada uma solução alcalina e inferior é considerada ácida."
ph_max_warning_text = "Atenção: Elevado pH na solução!"
ph_min_warning_text = "Atenção: Baixo pH na solução!"


#EC variables
ec_max = 2.0
ec_min = 0.5
ec_min_text   = "A Eletrocondutividade da solução está baixa, considere aumenta-la"
ec_ideal_text = "A Eletrocondutividade da solução está ideal!"
ec_max_text   = "A Eletrocondutividade da solução está alta, considere reduzi-la"
ec_description= "A Eletrocondutividade (EC) é a capacidade que a água possui de conduzir corrente elétrica. \
                Está normalmente relacionado com a presença de íões dissolvidos na água, que são partículas \
                com energia eléctrica própria. Quanto maior for a quantidade de iões dissolvidos, \
                maior será a condutividade elétrica. \n \
                Na Hidroponia, a EC é uma forma de quantificar os nutrientes que existem na água. \
                Quanto maior a quantidade de nutrientes, maior a Eletrocondutividade."
ec_max_warning_text = "Atenção: Elevada eletrocondutividade (EC) na solução!"
ec_min_warning_text = "Atenção: Baixa eletrocondutividade (EC) na solução!"


'''
    Do not change the next variables since they are used 
    in the notifications protocol
'''
#Air Temperature
temperature_max_warning = False
temperature_min_warning = False
temperature_max_type = "airTempMax"
temperature_min_type = "airTempMin"

#Water Temperature
water_temperature_max_warning = False
water_temperature_min_warning = False
water_temperature_max_type = "waterTempMax"
water_temperature_min_type = "waterTempMin"

#Humidity
humidity_max_warning = False
humidity_min_warning = False
humidity_max_type = "humidityMax"
humidity_min_type = "humidityMin"

#pH
ph_max_warning = False
ph_min_warning = False
ph_max_type = "phMax"
ph_min_type = "phMin"

#EC
ec_max_warning = False
ec_min_warning = False
ec_max_type = "ecMax"
ec_min_type = "ecMin"

# Array for booleans
warnings = [
    temperature_max_warning,
    temperature_min_warning,
    water_temperature_max_warning,
    water_temperature_min_warning,
    humidity_max_warning,
    humidity_min_warning,
    ph_max_warning,
    ph_min_warning,
    ec_max_warning,
    ec_min_warning
]

# Array for type
typesOfNot = [
    temperature_max_type,
    temperature_min_type,
    water_temperature_max_type,
    water_temperature_min_type,
    humidity_max_type,
    humidity_min_type,
    ph_max_type,
    ph_min_type,
    ec_max_type,
    ec_min_type
]
