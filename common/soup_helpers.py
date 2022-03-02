def text(doc):
    return (doc and doc.get_text()) or ''

def attr(doc, *possible_attr_names):
    attr_value = ''
    for attr_name in possible_attr_names:
        attr_value = doc and doc.get(attr_name)
        if attr_value:
            break
    return attr_value
