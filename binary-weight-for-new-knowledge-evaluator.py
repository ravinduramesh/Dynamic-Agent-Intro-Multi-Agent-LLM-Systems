import json

import re
import nltk
from nltk.stem import WordNetLemmatizer

jsonFilePaths = [
    # autogen llm selection
    "Existing-Solution/Responses/GPT-4o-backup1/autogen-llm-selection.json",
    "Existing-Solution/Responses/GPT-4o-backup2/autogen-llm-selection.json",
    "Existing-Solution/Responses/GPT-4o-backup3/autogen-llm-selection.json",
    # DRTAG llm selection
    "Novel-Approach/Responses/GPT-4o-backup1/DRTAG-llm-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup2/DRTAG-llm-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup3/DRTAG-llm-selection.json",
    # IAAG llm selection
    "Novel-Approach/Responses/GPT-4o-backup1/IAAG-llm-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup2/IAAG-llm-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup3/IAAG-llm-selection.json",
    # autogen random selection
    "Existing-Solution/Responses/GPT-4o-backup1/autogen-random-selection.json",
    "Existing-Solution/Responses/GPT-4o-backup2/autogen-random-selection.json",
    "Existing-Solution/Responses/GPT-4o-backup3/autogen-random-selection.json",
    # DRTAG random selection
    "Novel-Approach/Responses/GPT-4o-backup1/DRTAG-random-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup2/DRTAG-random-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup3/DRTAG-random-selection.json",
    # IAAG random selection
    "Novel-Approach/Responses/GPT-4o-backup1/IAAG-random-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup2/IAAG-random-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup3/IAAG-random-selection.json",
    # autogen round robin selection
    "Existing-Solution/Responses/GPT-4o-backup1/autogen-round-robin-selection.json",
    "Existing-Solution/Responses/GPT-4o-backup2/autogen-round-robin-selection.json",
    "Existing-Solution/Responses/GPT-4o-backup3/autogen-round-robin-selection.json",
    # DRTAG round robin selection
    "Novel-Approach/Responses/GPT-4o-backup1/DRTAG-round-robin-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup2/DRTAG-round-robin-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup3/DRTAG-round-robin-selection.json",
    # IAAG round robin selection
    "Novel-Approach/Responses/GPT-4o-backup1/IAAG-round-robin-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup2/IAAG-round-robin-selection.json",
    "Novel-Approach/Responses/GPT-4o-backup3/IAAG-round-robin-selection.json",
]

stopwords = set(nltk.corpus.stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text) # remove punctuation
    text = re.sub(r'\d+', '', text) # remove numbers
    text = ' '.join([word for word in text.split() if word not in stopwords])
    text = ' '.join([lemmatizer.lemmatize(word) for word in nltk.word_tokenize(text)])
    return text

vocab = {
    # Possible Illnesses
    "appendicitis", "gynecological", "kidney stone", "gastrointestinal", "colon cancer", "ileitis", "ovarian", "crohn disease", "colitis", "diverticulitis", "urinary tract", "musculoskeletal issue", "hernia",
    "cardiovascular", "gallbladder", "obstruction", "renal", "yersinia enterocolitica", "campylobacter jejuni", "ectopic pregnancy", "pelvic inflammatory", "endocrine disorder", "endometriosis", "inflammatory bowel",
    # Diagnostic Plans and Treatments 
    "clinical examination", "blood test", "stool test", "ct", "urinalysis", "ultrasound", "surgery", "antibiotic", "pain management", "manage pain", "pain relief", "physical examination", "pysical exam", "medical history", "nephrology",
    "endoscopic evaluation", "laparoscopy", "laparoscopic", "allergies", "anesthetic", "anesthesia", "pelvic exam", "neurological examination", "hormone level", "mri", "endoscopic evaluation", "probiotics", "urine",
    # Preventive Actions, Prior and Post Treatment Advice  
    "diet", "dietary", "hydrated", "hydration", "rest", "symptom diary", "fever", "nausea", "vomiting", "bowel", "dizziness", "abdominal rigidity", "stress", "breathing", "deepbreathing", "relaxation", "relax", "strenuous activity", "acupuncture", "allergy", "water", "diet", "heat", "fasting", "pain medication"
}

conversationScores = dict()

# Read data from the JSON file
for jsonFilePath in jsonFilePaths:
    with open(jsonFilePath, "r") as jsonFile:
        jsonData = json.load(jsonFile)

    initialAgents = {"Patient", "General-Ward-Doctor", "Nurse"}
    initialAgentsContent = ""
    autoGeneratedAgentsContent = ""

    for entry in jsonData:
        if entry["role"] in initialAgents:
            initialAgentsContent += entry["content"] + " "
            initialAgents.remove(entry["role"])
        else:
            autoGeneratedAgentsContent += entry["content"] + " "

    # Clean the text data and remove stopwords
    initialAgentsCleanedContent = clean_text(initialAgentsContent)
    autoGeneratedAgentsCleanedContent = clean_text(autoGeneratedAgentsContent)

    initialAgentsTermSet = set(initialAgentsCleanedContent.split())
    autoGeneratedAgentsTermSet = set(autoGeneratedAgentsCleanedContent.split())
    termsToScoreConversation = vocab.intersection(autoGeneratedAgentsTermSet - initialAgentsTermSet)

    filename = jsonFilePath.split("/")[-2] + '\n' + jsonFilePath.split("/")[-1]
    conversationScores[filename] = len(termsToScoreConversation)


# Plot a graph of conversation scores calculated using binary weighting for new knowledge
import matplotlib.pyplot as plt

plt.figure(figsize=(20, 10))
plt.rcParams.update({'font.size': 15})
barColors = []
for label in conversationScores.keys():
    if label.split("\n")[1].startswith("autogen"):
        barColors.append('orangered')
    elif label.split("\n")[1].startswith("DRTAG"):
        barColors.append('lawngreen')
    else:
        barColors.append('dodgerblue')

plt.bar(conversationScores.keys(), conversationScores.values(), color=barColors)
plt.xticks(rotation=90)
plt.ylabel("Conversation Score")
plt.title("Conversation scores calculated by binary weighting keywords in new dialogues.")
plt.tight_layout()
plt.savefig("conversationScoresBinaryWeighting2.png")
print("Graph is plotted successfully.")