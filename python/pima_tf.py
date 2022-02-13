
import pandas     as pd                                                                                            # Usado p/ ler e trabalhar com os dados csv
import tensorflow as tf                                                                                            # Usado p/ moldar e rodar a rede neural artificial
from   sklearn.model_selection import train_test_split                                                             # Usado p/ separar dados de treino dos de teste
from   pandas_profiling        import ProfileReport                                                                # Usado p/ extrair informações visuais dos dados
from   os                      import environ                                                                      # Usado p/ ocultar avisos desnecessários do tf
from   assets                  import brasao                                                                       # Autor, data etc

environ['TF_CPP_MIN_LOG_LEVEL'] = '1'                                                                              # Bloqueia INFOS e WARNING do tensoflow. ERROR continua

tam=8                                                                                                              # Define o numero de colunas do arquivo
drop_1=.24                                                                                                         # 1ª opção de dropout para evitar overfitting
drop_2=.26                                                                                                         # 2ª opção de dropout
arq     = 'assets/pima-indians-diabetes.csv'                                                                       # Nome do arquivo para leitura dos dados
legenda = ["Nº de gravidez", "Glicose", "Pressão sanguínea",                                                       # Dando nomes para as colunas dos dados
          "Trícepis", "Insulina", "IMC",
          "Chance de diabetes hereditária",
          "Idade", "Vive com diabetes"]


# O seguinte bloco serve para testar se o arquivo foi encontrado, caso contrário baixa da internet
try:
  open(arq,'r').close()
except FileNotFoundError:
  # Como o arquivo não é exatamente igual (há mais uma coluna e a primeira linha é de strings, que classificam
  # as colunas). Então temos que adaptar as seguintes variáveis:
  tam=9                                                                                                            # Números de colunas dos dados
  drop_1=0                                                                                                         # Não quero dropout
  drop_2=0                                                                                                         # Não quero dropout
  legenda.insert(-1,"Tipo sanguíneo")                                                                              # Insere string na penúltima coluna de "legenda"
  # A seguinte variável, informa o link para os dados online (note que é do github e é texto raw (puro))
  arq = 'https://raw.githubusercontent.com/PacktPublishing/Hands-on-Machine-Learning-with-TensorFlow/master/Section%203/pima-indians-diabetes.csv'
  
  nova_leg = ["Number_pregnant","Glucose_concentration","Blood_pressure","Triceps","Insulin","BMI",
              "Pedigree","Age","Group","Class"]                                                                    # Texto em inglês devido aos dados baixados

if tam == 9:
    pima          = pd.read_csv(arq, delimiter=',',header=0)                                                       # Lê e armazena dados na RAM
    pima          = pima[nova_leg]                                                                                 # Inverte colunas
    pima['Group'] = pima.Group.astype("category").cat.codes                                                        # Transforma letras em números
    pima.columns  = legenda                                                                                        # Traduz a 1 linha para português
    del nova_leg                                                                                                   # Deleta valores de 'nova_leg' da RAM
else:
    pima = pd.read_csv(arq,delimiter=',',header=0,names=legenda)                                                   # Lê e armazena dados na RAM

x = pima[legenda[0:tam]]                                                                                           # Valores de input (gravidez,...,tipo sanguíneo)
y = pima[legenda[tam]]                                                                                             # Valores de output (Vive com ou sem diabetes)
x = x.apply(lambda x: (x-x.min())/(x.max()-x.min()))                                                               # Normaliza os dados. Aumenta eficiencia da rede em achar padrões

# A seguinte linha divide as variáveis "x" para x_treino e x_teste e "y" para y_teste, ytreino. Note que
# por 'random_state','shuffle' e 'test_size' estão configuradas para os resultados serem reproduzíveis
x_treino, x_teste, y_treino, y_teste = train_test_split(x, y,random_state=101,shuffle=False,test_size =0.25)

'''
 AVISO: o seguinte comando não é necessário para a rede e serve apenas para termos noção do que há nos dados
 AVISO 2: o seguinte comando demora por menos de um minuto. Pode comenta-lá para acelerar o processo.
 AVISO 3: você pode abrir o arquivo "pima_site.html" no navegador
'''
info_pima = ProfileReport(pima)
info_pima.to_file("assets/pima_site.html")                                                                         # Extrai informações dos dados e plota em html


tf.random.set_seed(500)                                                                                            # Por motivo de reprodubilidade, fixamos o seed.

'''
 O bloco abaixo monta a arquitetura da rede.
 As funções 'Dense' são as camadas da arquitetura, o primeiro número indica quantos neurônios a camada têm.
 Desta forma, temos uma arq de 3 camadas e com as seguintes configurações:
 (12,8,1) caso o arquivo seja o local. - ou seja, 12 neurônios de entrada, 8 neurônios na única camada oculta, e 1 neurônio na camada de saída.
 (12,9,1) caso seja o arquivo baixado. - ou seja, 12 neurônios de entrada, 9 neurônios na única camada oculta, e 1 neurônio na camada de saída.
 As "activation" selecionam as funções que ativam os neurônios em cada camada
 Em relação ao 'swish' e 'softmax' eles apresentaram melhores resultados
 O 'Sigmoid' foi escolhido pois numa escolha binária, ele me fez mais sentido.
 As funções "Dropout" serve para evitar overfitting. Ele evita que uma proporção de neurônios sejam ativados
 A opção 'input_dim' informa o numero de dimensão dos dados, sabemos disso devido ao número de colunas de 'x'. 8 para o arquivo local e 9 para o baixado.
'''
model    =  tf.keras.models.Sequential([
            tf.keras.layers.Dense(12, input_dim=tam, activation='swish'),
            tf.keras.layers.Dropout(drop_1),
            tf.keras.layers.Dense(tam, activation='softmax'),
            tf.keras.layers.Dropout(drop_2),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

'''
 Aqui configuramos um otimizador para encontrar os minimos rapidamente;
 escolhemos a função 'loss' que nos permite dizer quão longe/perto a rede está alcançando.
 A 'metrics' não é usada durante o treino da rede, só quando está sendo testada. Ela serve para
 julgar a performance da rede.
'''
model.compile(optimizer='Adam',
            loss='binary_crossentropy',
            metrics=["BinaryAccuracy"])

print("\nModelo da rede: \033[33mPronto\033[0m.\n\033[33;7mWarning\033[0m: Synapses are \033[31;1;5mfiring\033[0m and \033[34;6mbursting\033[0m.\n")

'''
 Aqui mostramos para a rede os dados de treino, assim a rede tenta obter os melhores pesos e bias para
 ajustar a sua previsibilidade.
 Neste caso, escolhemos um batch de tamanho não muito grande, para aumentar a velocidade do processamento
 Também optamos por uma época grande, para melhorar o aprendizado da rede
 O 'verbose=0' serve para o tf não plotar o avanço da rede, também melhora a velociadade pois haverá menos
 interrupções no processador.
'''
model.fit(x_treino, y_treino, epochs=1200, batch_size=110,verbose=0)

'''
 Nos separamos os dados de "x" e "y" em "x_treino, x_teste, y_treino, y_teste". A rede treinou e viu
 os 'x_treinos' e 'y_treinos'. Agora vamos introduzir novos dados na rede, com isso podemos ver quantos ela
 é capaz de acertar.
'''
testes, acertos = model.evaluate(x_teste, y_teste,verbose=1)

# Aqui printamos os resultados
if (acertos*100) >= 80.:
    print("\nQuantidade de dados de teste = {0}\nQuantidade de dados de treino = {1}\n\033[96;1mAcertos\033[0m da rede: \033[94;1m{2:.1f}%\033[0m\n".format(len(x_teste),len(x_treino),acertos*100))
elif (acertos*100) >=60. and (acertos*100)<80.:
    print("\nQuantidade de dados de teste = {0}\nQuantidade de dados de treino = {1}\n\033[96;1mAcertos\033[0m da rede: \033[93;1m{2:.1f}%\033[0m\n".format(len(x_teste),len(x_treino),acertos*100))
else:
    print("\nQuantidade de dados de teste = {0}\nQuantidade de dados de treino = {1}\n\033[96;1mAcertos\033[0m da rede: \033[91;1m{2:.1f}%\033[0m\n".format(len(x_teste),len(x_treino),acertos*100))
