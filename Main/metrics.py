from rouge_score import rouge_scorer
import os
import textstat
import numpy as np

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

rouge_scores = []
readability_scores = []

# Hay que poner en docslos documentos en txt, y en summaries, summaries-1 y summaries-2 los resumenes hechos por los prompts
# ordenados ascendente del mas malo al mas pŕo (summaries: malo, summaries-2: pro)
for filename in os.listdir('docs'):
    doc = open(f'docs/{filename}', 'r').read()
    summary_2 = open(f'summaries-2/{filename}', 'r').read()
    summary_1 = open(f'summaries-1/{filename}', 'r').read()
    summary = open(f'summaries/{filename}', 'r').read()

    rouge_scores.append({
        'filename': filename,
        'scores_2': scorer.score(doc, summary_2),
        'scores_1': scorer.score(doc, summary_1),
        'scores': scorer.score(doc, summary)
    })

    readability_scores.append({
        'filename': filename,
        'doc': textstat.flesch_kincaid_grade(doc),
        'summary_2': textstat.flesch_kincaid_grade(summary_2),
        'summary_1': textstat.flesch_kincaid_grade(summary_1),
        'summary': textstat.flesch_kincaid_grade(summary)
    })

print(readability_scores)

# Now graph the rouge_scores using matplotlib
import matplotlib.pyplot as plt

prompt1_scores = [np.array([score['scores']['rouge1'][2] for score in rouge_scores]).mean(),
                    np.array([score['scores']['rouge2'][2] for score in rouge_scores]).mean(),
                    np.array([score['scores']['rougeL'][2] for score in rouge_scores]).mean()]

prompt2_scores = [np.array([score['scores_1']['rouge1'][2] for score in rouge_scores]).mean(),
                    np.array([score['scores_1']['rouge2'][2] for score in rouge_scores]).mean(),
                    np.array([score['scores_1']['rougeL'][2] for score in rouge_scores]).mean()]

prompt3_scores = [np.array([score['scores_2']['rouge1'][2] for score in rouge_scores]).mean(),
                    np.array([score['scores_2']['rouge2'][2] for score in rouge_scores]).mean(),
                    np.array([score['scores_2']['rougeL'][2] for score in rouge_scores]).mean()]

# Graph each array across the x axis
text = ['rouge1', 'rouge2', 'rougeL']
plt.plot(text, prompt1_scores, label='prompt1', color='red', marker='o', linestyle='dashed')
plt.plot(text, prompt2_scores, label='prompt2', color='blue', marker='o', linestyle='dashed')
plt.plot(text, prompt3_scores, label='prompt3', color='green', marker='o', linestyle='dashed')

plt.legend()
plt.show()
plt.clf()

doc_readability = np.array([score['doc'] for score in readability_scores]).mean()
prompt1_readability = np.array([score['summary'] for score in readability_scores]).mean()
prompt2_readability = np.array([score['summary_1'] for score in readability_scores]).mean()
prompt3_readability = np.array([score['summary_2'] for score in readability_scores]).mean()

plt.plot(['doc', 'prompt1', 'prompt2', 'prompt3'], [doc_readability, prompt1_readability, prompt2_readability, prompt3_readability], color='red', marker='o', linestyle='dashed')

plt.show()