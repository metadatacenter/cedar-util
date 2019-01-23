#!/usr/bin/python3

# Functions to normalize terms to make sure that the NCBO Annotator is able to annotate them
#


def normalize_value(term, norm_values):
    """
    Normalizes a term to ensure that the NCBO Annotator is able to annotate it
    :param value: 
    :param file_norm_values: File that contains some normalized values to help improve the annotation results
    """
    term = term.lower()
    term = term.replace('_', ' ')
    term = term.replace('uberon:', '')

    if norm_values is not None and term in norm_values and len(norm_values[term]) > 0:
        return norm_values[term]
    else:
        return term