# Target Json logs
print("Running Assigner..")
target_file = input("Which file?: ").strip()

# Import and setup
import json
import re
regex = r'\b\w+\b'

with open("training.json") as td:
    training_data = json.load(td)
    print("Training loaded..")

with open(target_file + '.json') as tf:
    raw_logs = json.load(tf)
    print("Logs loaded..")

#debug single word catcher
debug_short_words = []
#======================= Logic ============================
def keyword_search(logs):
    print("Running keyword search")
    for log in logs:

        if type(log["LOG"]) is not str:
            log["LOG"] = str(log["LOG"])
        current_confidence = 0
        current_category = "Unclassed"

        for category in training_data:
            this_confidence = 0
            this_category = category["category"]

            words = re.findall(regex, (log["LOG"]))
            matched_primary_words = []
            matched_secondary_words = []

            for word in words:
                if len(words) == 1:
                    if len(word) <=2 and category["category"] == "NOISE":
                        this_confidence += category["category_weighting"]

                word = word.lower()
                if word in category["primaryWords"]:
                    print("Found a word: " + word)
                    this_confidence += category["primary_keyword_weighting"]
                    matched_primary_words.append(word)

                elif word in category["secondaryWords"]:
                    print("Found a word: " + word)
                    this_confidence += category["secondary_keyword_weighting"]
                    matched_secondary_words.append(word)

                elif (word not in matched_primary_words and word not in matched_secondary_words) and (len(words) == 1 and category["category"] == "NOISE"):
                    this_confidence += category["category_weighting"]
                    debug_short_words.append(word)



            if len(matched_primary_words) > 0 and len(matched_secondary_words) in range(1,4):

                for p in matched_primary_words:
                    if p in words:
                        for s in matched_secondary_words:
                            if s in words:
                                if words.index(p) - words.index(s) in range(0,3):
                                  this_confidence += category["category_weighting"]


            if this_confidence > current_confidence:
                current_confidence = this_confidence
                current_category = this_category

        if current_category != "Unclassed":
            print("Category: " + current_category)
            build_model(log["ID"], log["LOG"], current_category)
        else:
            print("Not recognised")
            build_model(log["ID"], log["LOG"], "Not Recognised")

#===========================================================

results = []
def build_model(chat_id, chat_log, chat_category):
    model = {
    "chat_id": chat_id,
    "chat_log": chat_log,
    "chat_category": chat_category
    }
    results.append(model)


keyword_search(raw_logs)

#======================= Close ============================

# Save data
for i in results:
    if i['chat_category'] != "Unclassed":
       print("chat_id " + str(i['chat_id']) + " Recognised.. " + i["chat_category"])
    r = json.dumps(i)

    file = open(target_file + '_assigned.json', 'a')
    file.write(r + '\n')
    file.close()

#debug short words
print(debug_short_words)

print("end")
