import matplotlib.pyplot as plt
import io
import base64

def gerar_grafico_barras(labels, values, cores, titulo, ylabel, ylim=(0, 100)):
    # Cria uma nova figura do matplotlib com tamanho 8x4
    plt.figure(figsize=(8,4))
    # Gera as barras do gráfico com as labels, valores e cores fornecidos
    bars = plt.bar(labels, values, color=cores)
    # Define o título do gráfico
    plt.title(titulo)
    # Define o label do eixo Y
    plt.ylabel(ylabel)
    # Define o limite do eixo Y
    plt.ylim(*ylim)
    # Adiciona o valor acima de cada barra
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, value + 2, f'{value:.0f}', ha='center', va='bottom')
    # Cria um buffer de bytes para salvar a imagem
    buf = io.BytesIO()
    # Ajusta o layout para não cortar elementos
    plt.tight_layout()
    # Salva o gráfico no buffer em formato PNG
    plt.savefig(buf, format='png')
    # Fecha a figura para liberar memória
    plt.close()
    # Codifica a imagem em base64 para uso em HTML
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # Fecha o buffer
    buf.close()
    # Retorna a string base64 da imagem
    return image_base64
