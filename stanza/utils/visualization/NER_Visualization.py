from spacy import displacy
from spacy.tokens import Doc
from spacy.tokens import Span
from stanza.models.common.constant import is_right_to_left
import stanza
import spacy


def visualize_ner_doc(doc, pipeline, select=None, colors=None):
    """
    Takes a stanza doc object and language pipeline and visualizes the named entities within it.
    Stanza currently supports a limited amount of languages for NER, which you can view here:
    https://stanfordnlp.github.io/stanza/ner_models.html
    To view only a specific type(s) of named entities, set the optional 'select' argument to
    a list of the named entity types. Ex: select=["PER", "ORG", "GPE"] to only see entities tagged as Person(s),
    Organizations, and Geo-political entities. A full list of the available types can be found here:
    https://stanfordnlp.github.io/stanza/available_models.html (ctrl + F "The following table").
    """
    model, documents = spacy.blank('en'), []  # must install the latest version of spacy english model
    # link can be found here: https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.3.0
    sentences, rtl = doc.sentences, is_right_to_left(pipeline)
    if rtl:  # need to flip order of all the sentences in rendered display
        sentences = reversed(doc.sentences)
        # adjust colors to be in LTR flipped format
        if colors:
            for color in colors:
                clr_val = colors[color]
                colors.pop(color)
                colors["‮" + color[::-1]] = clr_val
    for sentence in sentences:
        words, display_ents, already_found = [], [], False
        # initialize doc object with words first
        for i, word in enumerate(sentence.words):
            if rtl and word.text.isascii() and not already_found:
                to_append = [word.text[::-1]]
                next_word_index = i + 1
                # account for flipping non Arabic words back to original form and order. two flips -> original order
                while next_word_index <= len(sentence.words) - 1 and sentence.words[next_word_index].text.isascii():
                    to_append.append(sentence.words[next_word_index].text[::-1])
                    next_word_index += 1
                to_append = reversed(to_append)
                for token in to_append:
                    words.append(token)
                already_found = True
            elif rtl and word.text.isascii() and already_found:  # skip over already collected words
                continue
            else:  # arabic chars
                words.append(word.text)
                already_found = False

        document = Doc(model.vocab, words=words)

        # tag all NER tokens found
        for ent in sentence.ents:
            if select and ent.type not in select:
                continue
            found_indexes = []
            for token in ent.tokens:
                found_indexes.append(token.id[0] - 1)
            if not rtl:
                to_add = Span(document, found_indexes[0], found_indexes[-1] + 1, ent.type)
            else:  # RTL languages need the override char to flip order
                to_add = Span(document, found_indexes[0], found_indexes[-1] + 1, "‮" + ent.type[::-1])
            display_ents.append(to_add)
        document.set_ents(display_ents)
        documents.append(document)

    # Visualize doc objects
    visualization_options = {"ents": select}
    if colors:
        visualization_options["colors"] = colors
    for document in documents:
        displacy.render(document, style='ent', options=visualization_options)


def visualize_ner_str(text, pipeline, select=None, colors=None):
    pipe = stanza.Pipeline(pipeline)
    doc = pipe(text)
    visualize_ner_doc(doc, pipeline, select, colors)


def main():
    # Test on En inputs
    visualize_ner_str('''Samuel Jackson, a Christian man from Utah, went to the JFK Airport for a flight to New York.
                               He was thinking of attending the US Open, his favorite tennis tournament besides Wimbledon.
                               That would be a dream trip, certainly not possible since it is $5000 attendance and 5000 miles away.
                               On the way there, he watched the Super Bowl for 2 hours and read War and Piece by Tolstoy for 1 hour.
                               In New York, he crossed the Brooklyn Bridge and listened to the 5th symphony of Beethoven as well as
                               "All I want for Christmas is You" by Mariah Carey.''', "en")
    visualize_ner_str("Barack Obama was born in Hawaii. He was elected President of the United States in 2008", 'en',
                      select=['PERSON', 'DATE'])
    visualize_ner_str("Barack Obama was born in Hawaii. He was elected President of the United States in 2008", 'en',
                      select=['PERSON', 'DATE'], colors={"PERSON": "yellow",
                                                         "DATE": "red", "GPE": "blue"})
    # test on Chinese inputs
    visualize_ner_str('''来自犹他州的基督徒塞缪尔杰克逊前往肯尼迪机场搭乘航班飞往纽约。
                             他正在考虑参加美国公开赛，这是除了温布尔登之外他最喜欢的网球赛事。
                             那将是一次梦想之旅，当然不可能，因为它的出勤费为 5000 美元，距离 5000 英里。
                             在去的路上，他看了 2 个小时的超级碗比赛，看了 1 个小时的托尔斯泰的《战争与碎片》。
                               在纽约，他穿过布鲁克林大桥，聆听了贝多芬的第五交响曲以及 玛丽亚凯莉的“圣诞节我想要的就是你”。''', "zh", colors={"PERSON": "yellow",
                                                                                                  "DATE": "red",
                                                                                                  "GPE": "blue"})
    # Test on R->L inputs
    visualize_ner_str("اسمي أليكس ، أنا من الولايات المتحدة.", "ar")
    visualize_ner_str(
        ".مرحبا اسمي أليكس. أنا لاعب تنس محترف من الولايات المتحدة الأمريكية. أنا أتنافس في بطولة ويمبلدون هذا العام",
        "ar")
    visualize_ner_str("ولد باراك أوباما في هاواي. انتخب رئيساً للولايات المتحدة الأمريكية عام 2008.", "ar")
    visualize_ner_str(
        ".أعيش في سان فرانسيسكو ، كاليفورنيا. اسمي أليكس وأنا ألتحق بجامعة ستانفورد. أنا أدرس علوم الكمبيوتر وأستاذي هو كريس مانينغ",
        'ar')
    visualize_ner_str(
        ".أعيش في سان فرانسيسكو ، كاليفورنيا. اسمي أليكس وأنا ألتحق بجامعة ستانفورد. أنا أدرس علوم الكمبيوتر وأستاذي هو كريس مانينغ",
        'ar', colors={"PER": "red", "LOC": "blue", "ORG": "yellow"})
    visualize_ner_str("""صامويل جاكسون ، رجل مسيحي من ولاية يوتا ، ذهب إلى مطار جون كنيدي في رحلة إلى نيويورك.
                               كان يفكر في حضور بطولة الولايات المتحدة المفتوحة للتنس ، بطولة التنس المفضلة لديه إلى جانب بطولة ويمبلدون.
                               ستكون هذه رحلة الأحلام ، وبالتأكيد ليست ممكنة لأنها تبلغ 5000 دولار للحضور و 5000 ميل.
                               في الطريق إلى هناك ، شاهد سوبر بول لمدة ساعتين وقرأ الحرب والسلام لتولستوي لمدة ساعة واحدة.
                               في نيويورك ، عبر جسر بروكلين واستمع أيضًا إلى السيمفونية الخامسة لبيتهوفن
                               "كل ما أريده لعيد الميلاد هو أنت" بقلم ماريا كاري.""", "ar",
                      colors={"PER": "pink", "LOC": "linear-gradient(90deg, #aa9cfc, #fc9ce7)", "ORG": "yellow"})


main()