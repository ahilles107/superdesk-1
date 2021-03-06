
import superdesk


def norvig_suggest(word, model):
    """Norvig's simple spell check.

    Modified not to return only best correction, but all of them sorted.
    """
    NWORDS = model
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def edits1(word):
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
        replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
        inserts = [a + c + b for a, b in splits for c in alphabet]
        return set(deletes + transposes + replaces + inserts)

    def known_edits2(word):
        return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

    def known(words):
        return set(w for w in words if w in NWORDS)

    def suggest(word):
        candidates = known([word]) or known(edits1(word))  # or known_edits2(word)
        return sorted(candidates, key=NWORDS.get, reverse=True)

    return suggest(word.lower())


class SpellcheckResource(superdesk.Resource):

    resource_methods = ['POST']
    item_methods = []

    schema = {
        'word': {'type': 'string', 'required': True},
        'dict': superdesk.Resource.rel('dictionaries', False),
    }

    # you should be able to make edits
    privileges = {'POST': 'archive'}


class SpellcheckService(superdesk.Service):

    def suggest(self, word, dict_id):
        dictionary = superdesk.get_resource_service('dictionaries').find_one(req=None, _id=dict_id)
        if not dictionary:
            return []
        return norvig_suggest(word, dictionary['content'])

    def create(self, docs, **kwargs):
        for doc in docs:
            doc['corrections'] = self.suggest(doc['word'], doc.get('dict'))
        return [doc['word'] for doc in docs]
