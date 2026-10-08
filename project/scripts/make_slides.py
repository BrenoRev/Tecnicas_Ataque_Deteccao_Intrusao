"""Apresentação do projeto em PPTX, no modelo de slides do CIn, e roteiro da fala.

Não treina nada e não lê results/. Parte do arquivo-modelo do CIn (tema,
layouts e logotipos), remove os slides de exemplo e monta os slides com:

- as figuras de report/figures/ (PNG), geradas por scripts/make_report_assets.py;
- tabelas nativas montadas com as células de report/tables/<nome>.csv;
- tópicos curtos, escritos aqui e conferidos contra as mesmas tabelas.

Escreve report/apresentacao.pptx e report/roteiro.md (tempo e pontos da fala de
cada slide, com a soma). Só usa caixas de texto, imagens e tabelas nativas, para
o arquivo abrir no Google Slides.

O python-pptx fica no grupo de dependências "slides", fora do ambiente dos
experimentos.

Uso: uv run --group slides python scripts/make_slides.py
"""

import csv
import io
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.util import Emu, Pt

from doh_ids.config import PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "report"
TEMPLATE = PROJECT_ROOT.parent / "geracao_latex_and_pdf" / "Apresentação Padrão CIn-UFPE.pptx"
OUTPUT = REPORT_DIR / "apresentacao.pptx"
SCRIPT_OUTPUT = REPORT_DIR / "roteiro.md"

# Cores e fontes dos slides de exemplo do modelo do CIn.
DARK = RGBColor(0x23, 0x1F, 0x20)
RED = RGBColor(0xAF, 0x04, 0x21)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xEE, 0xEE, 0xEE)
FONT = "Proxima Nova"
FONT_TITLE = "Proxima Nova Extrabold"

# Geometria em EMU. O slide do modelo tem 9144000 x 5143500 (16:9).
SLIDE_WIDTH = 9144000
SLIDE_HEIGHT = 5143500
MARGIN = 311700
BAND_HEIGHT = 860000
BODY_TOP = 1010000
BODY_HEIGHT = 3900000
LEFT_WIDTH = 4000000
RIGHT_LEFT = 4500000
RIGHT_WIDTH = SLIDE_WIDTH - RIGHT_LEFT - MARGIN
FULL_WIDTH = SLIDE_WIDTH - 2 * MARGIN
WIDE_VISUAL_HEIGHT = 2500000

# Posição, no modelo, do slide de onde sai o logotipo branco do CIn.
LOGO_WHITE_SLIDE = 0

DECIMAL_POINT = re.compile(r"(?<=\d)\.(?=\d)")

LAYOUT_TITLE = "TITLE"
LAYOUT_TITLE_ONLY = "TITLE_ONLY"

COVER_TITLE = "IDS explicável para ataques DNS over HTTPS"
COVER_SUBTITLE = "Reprodução, segundo dataset e modificação"
PROFESSOR = "Prof. Paulo Freitas de Araujo Filho · CIn/UFPE"
TEAM = "Amanda Arruda · Breno Silva Xavier de Souza · João Henrique Portela · Antonio Gonzaga"
COURSE = "CIN0114 · Técnicas de Ataque e Detecção de Intrusão · 2026.2"
REPOSITORY = "github.com/BrenoRev/Tecnicas_Ataque_Deteccao_Intrusao"

# Cada slide: título, tempo da fala em segundos, tópicos, elemento visual e os
# pontos da fala que vão para as anotações e para o roteiro. "figure" é o nome
# de um PNG de report/figures; "table" é (csv, colunas, linhas, rótulos).
SLIDES = [
    {
        "title": "O artigo em um slide",
        "seconds": 55,
        "bullets": [
            "Problema: o DoH cifra a consulta DNS; o túnel DNS vira HTTPS comum",
            "O IDS só tem estatísticas de fluxo: 29 atributos, sem decifrar o TLS",
            "Três classes: Non-DoH, Benign-DoH, Malicious-DoH",
            "Sistema: três subconjuntos balanceados com SMOTE, três Random Forests "
            "e uma regressão logística que os combina",
            "Explicação das decisões com SHAP, em painel interativo",
            "Publicado: precisão, recall e F1 acima de 99,9%",
        ],
        "talk": [
            "A turma já viu o seminário: só o necessário para entender o que reproduzimos.",
            "Artigo: Zebin, Rezvy e Luo, IEEE TIFS, 2022. Dataset CIRA-CIC-DoHBrw-2020.",
            "Os valores acima de 99,9% são os do resumo do artigo.",
        ],
    },
    {
        "title": "O que construímos",
        "seconds": 55,
        "bullets": [
            "Reimplementação a partir do texto: o código público só traz o painel "
            "e um Random Forest único",
            "Duas leituras da profundidade das árvores, lado a lado: 5 (Seção IV-B) "
            "e variável (Algoritmo 1)",
            "Todas as tabelas e figuras de resultado do artigo, com a diferença medida",
            "Segundo dataset: CIRA + HKD, com três ferramentas de túnel novas",
            "Protocolo corrigido: 10 seeds, teste sem vetores repetidos, folds por máquina",
            "Modificação do sistema e teste de robustez",
            "Um script por experimento; resultado gravado com seed, versões e commit",
        ],
        "talk": [
            "Nada foi ajustado para aproximar número do artigo: seed, hiperparâmetro e "
            "limpeza ficaram fixos.",
            "As duas leituras de profundidade têm apoio no texto; reportamos as duas.",
            "As etapas seguintes usam a leitura de profundidade variável como base, porque "
            "a outra não prediz uma das classes.",
        ],
    },
    {
        "title": "Dados e protocolo",
        "seconds": 45,
        "bullets": [
            "Remover linhas com valor ausente reproduz a Tabela I do artigo",
            "Split 90/10 estratificado, seed 42",
            "Validação cruzada de 10 folds dentro do treino",
            "Segundo dataset: só a classe maliciosa ganha tráfego novo",
            "No CIRA, o malicioso vem de outras máquinas e de outro período",
        ],
        "tables": [
            (
                "dados_cira_contagens",
                ["Conjunto", "Non-DoH", "Benign-DoH", "Malicious-DoH"],
                ["Limpo", "Tabela I", "Reprodução: treino", "Reprodução: teste"],
                ["CIRA limpo", "Tabela I do artigo", "CIRA: treino", "CIRA: teste"],
            ),
            (
                "dados_segundo_contagens",
                ["Conjunto", "Non-DoH", "Benign-DoH", "Malicious-DoH"],
                ["Sem réplicas: treino", "Sem réplicas: teste", "HKD isolado: teste"],
                ["Combinado: treino", "Combinado: teste", "HKD isolado"],
            ),
        ],
        "talk": [
            "Não há conjunto de validação separado, como no artigo: a validação é cruzada.",
            "O combinado publicado repete 20 vezes cada fluxo do HKD; usamos a forma sem "
            "réplicas, para o teste não conter cópias do treino.",
            "O HKD sozinho só tem tráfego malicioso: serve de teste na transferência.",
        ],
    },
    {
        "title": "Reprodução: as duas leituras ao lado da Fig. 4b",
        "seconds": 65,
        "figure": "matriz_confusao_teste_dupla",
        "wide": True,
        "bullets": [
            "Profundidade 5: nenhum Benign-DoH predito, e a acurácia ainda é 97,79%",
            "Profundidade variável: a 553 fluxos da matriz do artigo, contra 4711",
            "A proximidade não diz qual configuração os autores usaram",
        ],
        "talk": [
            "Linha é a classe real, coluna a predita; entre parênteses, a diferença para o artigo.",
            "Trilha fiel é a profundidade 5; trilha variante, a profundidade variável.",
            "Com profundidade 5, os 1975 fluxos Benign-DoH do teste vão para Non-DoH.",
            "Com profundidade variável: F1 macro de 96,56%, contra 97,82% calculado da Fig. 4b.",
            "Não afirmamos que a profundidade variável é a dos autores: são duas leituras "
            "com apoio no texto.",
        ],
    },
    {
        "title": "Por que a profundidade 5 perde uma classe",
        "seconds": 55,
        "bullets": [
            "Sozinhos, os três Random Forests acertam 85% a 86% do Benign-DoH",
            "A perda acontece na regressão logística que os combina",
            "No treino, quando os três dizem Benign-DoH, a classe real mais comum é Non-DoH",
            "A acurácia esconde a classe rara: Benign-DoH é 1,70% do teste",
        ],
        "tables": [
            (
                "reproducao_metricas",
                ["Métrica", "Artigo", "Prof. 5", "Prof. var."],
                [
                    "Benign-DoH: precisão",
                    "Benign-DoH: recall",
                    "Malicious-DoH: recall",
                    "Acurácia",
                    "F1 macro",
                ],
                None,
            )
        ],
        "talk": [
            "Os bases de profundidade 5 têm precisão de Benign-DoH perto de 30%: marcam "
            "muito Non-DoH como Benign-DoH.",
            "A combinação em que os três dizem Benign-DoH ocorre em 49247 linhas do "
            "treino; 31025 são Non-DoH. O meta-classificador devolve Non-DoH.",
            "Por isso as métricas por classe vêm antes das médias, e a média é a macro.",
        ],
    },
    {
        "title": "Tabela II e ferramenta de túnel",
        "seconds": 55,
        "bullets": [
            "A Tabela II do artigo (99,98%) diverge da matriz do próprio artigo (99,78%)",
            "A ordem dos modelos de comparação se mantém em F1 macro",
            "Ferramenta de túnel (Seção VI-D): recall a menos de 2 pontos do artigo "
            "com profundidade variável",
            "O artigo não descreve esse método: é leitura nossa",
        ],
        "tables": [
            (
                "tabela2_superior_macro_dupla",
                ["Modelo", "Acurácia Art.", "Acurácia Rep.", "F1 Art.", "F1 Macro"],
                None,
                None,
            )
        ],
        "talk": [
            "Art. é o valor do artigo; Rep. e Macro são a reprodução, com média macro.",
            "O artigo não diz que média usa; nenhuma média reproduz a linha do modelo proposto.",
            "A legenda da Fig. 9 só é reproduzida com os arquivos sem a limpeza: é "
            "indício, não prova, de que essa seção usou outros dados.",
        ],
    },
    {
        "title": "Explicabilidade com SHAP",
        "seconds": 55,
        "figure": "shap_importancia_cira",
        "bullets": [
            "Artigo: Duration em primeiro. Aqui: PacketLengthMode, com larga margem",
            "Correlação de Spearman com a Fig. 5: 0,62 e 0,51",
            "Quatro valores de PacketLengthMode cobrem 99,84% do malicioso do CIRA",
            "Duration: direção do artigo confirmada; o sinal troca em 33,13 s na nossa amostra",
            "O SHAP explica os Random Forests base, não o empilhamento",
        ],
        "talk": [
            "Uma regra com um só atributo teria recall de 99,84% e 1 falso positivo em "
            "909555 fluxos legítimos: o modelo pode separar pela captura.",
            "Não dizemos que o limiar de 40 s foi refutado: a amostra tem classes em "
            "partes iguais e o artigo lê o valor a olho.",
            "O painel interativo foi implementado e pode ser mostrado ao final.",
        ],
    },
    {
        "title": "Protocolo corrigido: 10 seeds",
        "seconds": 50,
        "figure": "corrigido_seeds",
        "bullets": [
            "A: sistema do artigo, profundidade variável. F1 macro de 96,56 ± 0,12%",
            "B e C: Random Forest único com SMOTE; M1M2: a nossa modificação",
            "13,64% do teste repete um vetor do treino; sem eles, os vereditos não mudam",
            "Folds por máquina: recall de Benign-DoH cai de 93,07% para 31,10%",
        ],
        "talk": [
            "Um ponto por seed; o traço é a média.",
            "Com profundidade 5, o recall de Benign-DoH é zero nas dez seeds.",
            "A separação entre Non-DoH e Benign-DoH aprendida em três máquinas não vale na quarta.",
            "Nenhuma máquina gerou tráfego legítimo e malicioso: nenhum split separa a "
            "captura do ataque.",
        ],
    },
    {
        "title": "Segundo dataset: ferramentas novas",
        "seconds": 65,
        "figure": "segundo_recall_ferramenta",
        "bullets": [
            "Treinado no CIRA, o sistema detecta 1,81% dos fluxos do HKD",
            "A regra de PacketLengthMode: 99,84% no CIRA, 0% no HKD",
            "Retreino sem réplicas: 99,42%, em fluxos vizinhos dos do treino",
            "Retreino no publicado: todo fluxo do HKD no teste tem cópia no treino",
            "Com profundidade 5: 73,29% nas ferramentas do HKD",
        ],
        "talk": [
            "É o achado principal. É compatível com um detector que aprendeu a assinatura "
            "das ferramentas e da captura do CIRA, e não o comportamento de túnel.",
            "Os 99,42% são 510 de 513 fluxos, e medem as mesmas ferramentas, não uma nunca vista.",
            "Non-DoH e Benign-DoH do combinado são os do CIRA: métricas gerais iguais são "
            "esperadas.",
        ],
    },
    {
        "title": "Modificação: Random Forest único com peso de classe",
        "seconds": 60,
        "bullets": [
            "Sem SMOTE e sem empilhamento; M1M2 também seleciona hiperparâmetros",
            "F1 macro 0,50 ponto acima no CIRA e 0,57 no combinado, nas dez seeds",
            "O ganho já está em M1, que treina em 31 s",
            "A seleção de hiperparâmetros não muda o F1 macro: −0,08 ± 0,15 ponto",
        ],
        "tables": [
            (
                "modificacao_metricas_dupla",
                ["Dataset", "Modelo", "Benign prec.", "Benign rec.", "F1 macro", "Treino (s)"],
                [("CIRA", "A"), ("CIRA", "M1"), ("CIRA", "M1M2")]
                + [("Combinado sem réplicas", "A"), ("Combinado sem réplicas", "M1M2")],
                None,
            )
        ],
        "wide": True,
        "talk": [
            "A é o sistema do artigo com profundidade variável; 10 seeds, média e desvio.",
            "M1 perde 0,50 ponto de recall de Benign-DoH em relação a A.",
            "Não dizemos que a modificação reduz falsos positivos: no CIRA é cerca de um "
            "fluxo por teste, e não se repete no combinado.",
            "Os testes das seeds se sobrepõem: não usamos a palavra significativo.",
        ],
    },
    {
        "title": "Robustez: fragmentação simulada do fluxo",
        "seconds": 50,
        "figure": "robustez_fragmentacao",
        "bullets": [
            "O artigo publica que a duração pesa: o atacante encurta o fluxo",
            "Duração e bytes divididos por k, no espaço de atributos",
            "k = 2: o sistema do artigo perde 3,19 pontos de recall; M1M2, 0,34",
            "k ≥ 4: M1M2 desaba em duas ou três seeds",
            "Não ordena os modelos em robustez",
        ],
        "talk": [
            "Nenhum tráfego foi gerado: é perturbação simulada, sem retreino.",
            "Nos fatores 8 e 16, mais de 96% dos vetores são fisicamente incoerentes.",
            "Não dizemos quanto um atacante real evadiria.",
        ],
    },
    {
        "title": "Limitações e conclusão",
        "seconds": 60,
        "bullets": [
            "A reprodução depende de um ponto que o artigo deixa em aberto",
            "A Tabela II e o resumo do artigo não foram reproduzidos por nenhuma leitura",
            "O sistema não generaliza para ferramentas fora do treino",
            "Um atributo separa quase todo o malicioso do CIRA: captura e classe se confundem",
            "Um Random Forest único com peso de classe supera o empilhamento em F1 macro",
            "Nossa parte: reprodução com uma seed; fragmentação só simulada",
            "Próximo passo: gerar tráfego fragmentado e testar ferramenta deixada de fora",
        ],
        "talk": [
            "A modificação melhora o F1 macro em meio ponto e não resolve a generalização.",
            "O segundo dataset compartilha duas classes com o primeiro.",
            "Relatório, código e resultados estão no repositório.",
        ],
    },
]


def template_logo(presentation: Presentation, slide_index: int) -> io.BytesIO:
    """Imagem do logotipo do CIn guardada em um slide de exemplo do modelo."""
    slide = presentation.slides[slide_index]
    pictures = [shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
    assert pictures, f"slide {slide_index + 1} do modelo sem imagem"
    largest = max(pictures, key=lambda shape: shape.width)
    return io.BytesIO(largest.image.blob)


def remove_all_slides(presentation: Presentation) -> None:
    """Tira do arquivo os slides de exemplo e o de orientações do modelo."""
    slide_ids = presentation.slides._sldIdLst
    for slide_id in list(slide_ids):
        presentation.part.drop_rel(slide_id.rId)
        slide_ids.remove(slide_id)


def layout_named(presentation: Presentation, name: str):
    """Layout do modelo com o nome dado."""
    return next(layout for layout in presentation.slide_layouts if layout.name == name)


def add_background(slide, color: RGBColor, height: int = SLIDE_HEIGHT) -> None:
    """Retângulo de fundo, do topo do slide até a altura dada, atrás de tudo."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    # O primeiro lugar na árvore de formas é o fundo: os textos ficam por cima.
    tree = slide.shapes._spTree
    tree.remove(shape._element)
    tree.insert(2, shape._element)


def write_lines(text_frame, lines: list[str], size: int, color: RGBColor, **font) -> None:
    """Escreve um parágrafo por linha, com a fonte do modelo."""
    text_frame.word_wrap = True
    for index, line in enumerate(lines):
        paragraph = text_frame.paragraphs[0] if index == 0 else text_frame.add_paragraph()
        paragraph.space_after = Pt(font.get("space_after", 0))
        run = paragraph.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = font.get("name", FONT)
        run.font.bold = font.get("bold", False)


def add_text(slide, lines: list[str], box: tuple[int, int, int, int], size: int, **font) -> None:
    """Caixa de texto nativa na posição (esquerda, topo, largura, altura)."""
    shape = slide.shapes.add_textbox(*box)
    write_lines(shape.text_frame, lines, size, font.pop("color", DARK), **font)


def add_title(slide, title: str) -> None:
    """Faixa escura no topo com o título, no espaço reservado do layout."""
    add_background(slide, DARK, BAND_HEIGHT)
    placeholder = slide.shapes.title
    placeholder.left, placeholder.top = MARGIN, 150000
    placeholder.width, placeholder.height = FULL_WIDTH, 560000
    placeholder.text_frame.clear()
    write_lines(placeholder.text_frame, [title], 24, WHITE, name=FONT_TITLE)


def add_figure(slide, name: str, box: tuple[int, int, int, int]) -> None:
    """Figura PNG do relatório, centralizada na caixa, sem deformar."""
    left, top, width, height = box
    picture = slide.shapes.add_picture(str(REPORT_DIR / "figures" / f"{name}.png"), left, top)
    scale = min(width / picture.width, height / picture.height)
    picture.width, picture.height = int(picture.width * scale), int(picture.height * scale)
    picture.left = left + (width - picture.width) // 2
    picture.top = top + (height - picture.height) // 2


def table_cells(name: str, columns: list[str], rows: list | None, labels: list[str] | None):
    """Células de report/tables/<name>.csv: as colunas e as linhas pedidas.

    Uma linha é pedida pelo valor da primeira coluna, ou por uma tupla com os
    valores das primeiras colunas. `labels` troca o texto da primeira coluna.
    Devolve só o corpo, sem o cabeçalho, com vírgula decimal.
    """
    with (REPORT_DIR / "tables" / f"{name}.csv").open(encoding="utf-8", newline="") as file:
        header, *lines = list(csv.reader(file))
    by_key = {}
    for line in lines:
        by_key[line[0]] = line
        by_key[tuple(line[:2])] = line
    selected = [by_key[row] for row in rows] if rows else lines
    indexes = [header.index(column) for column in columns]
    # Vírgula decimal só entre dois algarismos: "prof. 5" fica como está.
    body = [[DECIMAL_POINT.sub(",", line[index]) for index in indexes] for line in selected]
    for line, label in zip(body, labels or [], strict=False):
        line[0] = label
    return body


def add_table(slide, tables: list[tuple], box: tuple[int, int, int, int], size: int) -> None:
    """Tabela nativa com o cabeçalho da primeira tabela e as linhas de todas."""
    left, top, width, height = box
    # Folga à direita: há visualizadores que somam espaço entre as células.
    width = int(width * 0.93)
    header = tables[0][1]
    body = [line for table in tables for line in table_cells(*table)]
    row_height = min(height // (len(body) + 1), 330000)
    frame = slide.shapes.add_table(
        len(body) + 1, len(header), left, top, width, row_height * (len(body) + 1)
    )
    first_width = int(width * (0.34 if len(header) < 5 else 0.26))
    for index, column in enumerate(frame.table.columns):
        column.width = first_width if index == 0 else (width - first_width) // (len(header) - 1)
    for row_index, line in enumerate([header, *body]):
        frame.table.rows[row_index].height = row_height
        for column_index, value in enumerate(line):
            cell = frame.table.cell(row_index, column_index)
            cell.fill.solid()
            cell.fill.fore_color.rgb = DARK if row_index == 0 else (LIGHT, WHITE)[row_index % 2]
            cell.margin_top = cell.margin_bottom = Emu(30000)
            color = WHITE if row_index == 0 else DARK
            write_lines(cell.text_frame, [value], size, color, bold=row_index == 0)


def add_cover(presentation: Presentation, logo: io.BytesIO) -> None:
    """Slide de título: projeto, disciplina e equipe."""
    slide = presentation.slides.add_slide(layout_named(presentation, LAYOUT_TITLE))
    add_background(slide, DARK)
    slide.shapes.add_picture(logo, MARGIN, 300000, height=760000)
    title, subtitle = slide.placeholders[0], slide.placeholders[1]
    title.left, title.top, title.width, title.height = MARGIN, 1350000, FULL_WIDTH, 1500000
    title.text_frame.clear()
    write_lines(title.text_frame, [COVER_TITLE], 34, WHITE, name=FONT_TITLE)
    subtitle.left, subtitle.top = MARGIN, 2950000
    subtitle.width, subtitle.height = FULL_WIDTH, 1700000
    subtitle.text_frame.clear()
    people = [COVER_SUBTITLE, COURSE, PROFESSOR, TEAM]
    write_lines(subtitle.text_frame, people, 15, WHITE, space_after=5)
    slide.notes_slide.notes_text_frame.text = "Apresentar a equipe e o artigo reproduzido."


def add_content(presentation: Presentation, spec: dict) -> None:
    """Slide de conteúdo: título, tópicos e, se houver, figura ou tabela."""
    slide = presentation.slides.add_slide(layout_named(presentation, LAYOUT_TITLE_ONLY))
    add_title(slide, spec["title"])
    visual = spec.get("figure") or spec.get("tables")
    wide = spec.get("wide", False)
    if visual and wide:
        visual_box = (MARGIN, BODY_TOP, FULL_WIDTH, WIDE_VISUAL_HEIGHT)
        text_top = BODY_TOP + WIDE_VISUAL_HEIGHT + 80000
        text_box = (MARGIN, text_top, FULL_WIDTH, SLIDE_HEIGHT - text_top - 150000)
    elif visual:
        visual_box = (RIGHT_LEFT, BODY_TOP, RIGHT_WIDTH, BODY_HEIGHT)
        text_box = (MARGIN, BODY_TOP, LEFT_WIDTH, BODY_HEIGHT)
    else:
        text_box = (MARGIN, BODY_TOP, FULL_WIDTH, BODY_HEIGHT)
    bullets = [f"• {bullet}" for bullet in spec["bullets"]]
    add_text(slide, bullets, text_box, 16 if visual else 17, space_after=8)
    if spec.get("figure"):
        add_figure(slide, spec["figure"], visual_box)
    if spec.get("tables"):
        add_table(slide, spec["tables"], visual_box, 11)
    slide.notes_slide.notes_text_frame.text = "\n".join(spec["talk"])


def add_closing(presentation: Presentation, logo: io.BytesIO) -> None:
    """Slide final, com o endereço do repositório."""
    slide = presentation.slides.add_slide(layout_named(presentation, LAYOUT_TITLE_ONLY))
    add_background(slide, RED)
    slide.shapes.add_picture(logo, MARGIN, 300000, height=760000)
    placeholder = slide.shapes.title
    placeholder.left, placeholder.top = MARGIN, 1900000
    placeholder.width, placeholder.height = FULL_WIDTH, 900000
    placeholder.text_frame.clear()
    write_lines(placeholder.text_frame, ["Obrigado! Perguntas?"], 40, WHITE, name=FONT_TITLE)
    add_text(slide, [REPOSITORY], (MARGIN, 3000000, FULL_WIDTH, 400000), 16, color=WHITE)
    slide.notes_slide.notes_text_frame.text = "Abrir para perguntas."


def script_markdown() -> str:
    """Roteiro: tempo e pontos da fala de cada slide, com a soma dos tempos."""
    entries = [("Título e equipe", 30, ["Apresentar a equipe e o artigo reproduzido."])]
    entries += [(spec["title"], spec["seconds"], spec["talk"]) for spec in SLIDES]
    entries.append(("Encerramento", 10, ["Abrir para perguntas."]))
    total = sum(seconds for _, seconds, _ in entries)
    lines = [
        "# Roteiro da apresentação",
        "",
        "Gerado por `scripts/make_slides.py`, com os mesmos textos das anotações dos slides. "
        "Não edite à mão: mude o script e rode de novo.",
        "",
        f"Tempo disponível: 15 minutos. Soma dos tempos: {total // 60} min {total % 60:02d} s.",
        "",
        "Quem fala em cada slide: [Preencher: divisão da fala entre os quatro integrantes].",
    ]
    for number, (title, seconds, talk) in enumerate(entries, start=1):
        lines += ["", f"## {number}. {title} ({seconds // 60}:{seconds % 60:02d})", ""]
        lines += [f"- {point}" for point in talk]
    return "\n".join(lines) + "\n"


def main() -> None:
    """Monta a apresentação e o roteiro em report/."""
    presentation = Presentation(str(TEMPLATE))
    assert (presentation.slide_width, presentation.slide_height) == (SLIDE_WIDTH, SLIDE_HEIGHT)
    logo_white = template_logo(presentation, LOGO_WHITE_SLIDE)
    remove_all_slides(presentation)
    add_cover(presentation, logo_white)
    for spec in SLIDES:
        add_content(presentation, spec)
    logo_white.seek(0)
    add_closing(presentation, logo_white)
    presentation.save(str(OUTPUT))
    SCRIPT_OUTPUT.write_text(script_markdown(), encoding="utf-8")
    print(f"{len(presentation.slides)} slides em {OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"roteiro em {SCRIPT_OUTPUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
