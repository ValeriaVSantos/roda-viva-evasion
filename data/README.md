# Data

## Source

Transcripts from the [Roda Viva corpus](https://github.com/LeGOS-UFSCar/Roda-Viva) (LeGOS-UFSCar, University of São Carlos).

Roda Viva is a Brazilian political interview program broadcast since 1986 on TV Cultura. The corpus covers 11 politicians: Aécio Neves, Alexandre de Moraes, Anthony Garotinho, Ciro Gomes, Fernando Collor de Mello, José Dirceu, José Serra, Luiz Inácio Lula da Silva, Marina Silva, Michel Temer, and Sérgio Cabral.

## Annotated Dataset

The annotated file `pares_qa_anotacao.csv` contains 276 question-answer pairs with the following columns:

| Column | Type | Description |
|---|---|---|
| `ENTREVISTADO` | string | Politician name |
| `PERGUNTA` | string | Journalist question (full text) |
| `RESPOSTA` | string | Politician response (full text) |
| `PRE_ANOTACAO` | string | Heuristic pre-annotation (RESPONDE/PARCIAL/ESQUIVA) |
| `ANOTACAO_HUMANA` | string | Gold standard label |

### Label Distribution

| Label | Count | % |
|---|---|---|
| RESPONDE | 154 | 55.8% |
| PARCIAL | 100 | 36.2% |
| ESQUIVA | 22 | 8.0% |
| **Total** | **276** | **100%** |

### Annotation Guidelines

Labels were assigned based on the **central communicative goal** of the journalist's question:

- **RESPONDE**: The politician directly addresses the central point of the question.
- **PARCIAL**: The politician addresses the topic but avoids key aspects or introduces significant digressions.
- **ESQUIVA**: The politician redirects to a different topic, responds to a different question, or uses rhetorical strategies to avoid the central point.

## Access

Due to copyright restrictions on the original Roda Viva transcripts, the annotated dataset is available upon request. Please contact the authors.

To access the original transcripts, see the [LeGOS-UFSCar/Roda-Viva](https://github.com/LeGOS-UFSCar/Roda-Viva) repository.
