"""
Anki add-on to filter search result by only including notes
that have duplicate field entries with other notes in the search result

Usage:
- Add tag "dups:" before your search prompt (without ")

Example:
- Search for "dups:deck:current"
- The result will include a note of your current deck iff there exists another note of your current deck and both notes
  have the same note type id and identical content in any of the fields
- eg. notes "Front: richtig, Back: giusto" and "Front: richtig, Back: correto" are duplicate
- eg. notes "Front: richtig, Back: giusto" and "Front: richtig, Back: esatto, Extra: abc" are not duplicate (note ids)
- eg. notes "Front: richtig, Back: giusto" and "Front: giusto, Back: richtig" are not duplicate (field entries)
"""

from aqt import mw
from aqt.gui_hooks import browser_will_search, browser_did_search
from aqt.browser import SearchContext


# Global variables
applyFilter = False


def check_dups_filter(ctx: SearchContext) -> None:
    """
    Checks if dups search filter is present and saves state
    :param ctx: Current Search Context given by hook
    :return: None
    """

    global applyFilter
    applyFilter = False  # reset state

    # Ignore if ids are already set
    if ctx.ids is not None:
        return

    # Search for term
    term = ctx.search
    tag = "dups:"
    if not term.startswith(tag):
        return

    # Remove term from search
    ctx.search = ctx.search[len(tag):]

    # Save new state (next invocation of filter_result will know that search tag was present)
    applyFilter = True


def get_dup_ids(notes) -> set:
    """
    :return: Set of card ids that have duplicate field entries
    """

    # dictionary of (tuple(note_type, field_name) -> dict(field_entry -> note_id))
    cards = dict()

    # set of ids with duplicate fields
    ids = set()

    # Iterate all note ids
    for note_id in notes:

        # Get note from id
        note = mw.col.get_note(note_id)
        note_type_id = note.mid  # Note type id
        field_names = mw.col.models.field_names(note.note_type())  # Get note type field names

        # Iterate pairs of field_name and field_entry
        for name, field in zip(field_names, note.fields):

            # Build key (type_id and field_name)
            key = (note_type_id, name)

            if key not in cards:
                # Insert new inner dict if not yet present
                cards[key] = dict()

            if field in cards[key]:
                # If field was already added (so there is a duplicate)
                ids.add(note_id)  # add current card id
                ids.add(cards[key][field])  # add already visited card id
            else:
                cards[key][field] = note_id  # add new entry and save note_id

    # Return set of card ids that have duplicate field entries
    return ids


def filter_result(ctx: SearchContext) -> None:
    """
    Filters search result for only containing notes that have duplicate field entries
    :param ctx: Current Search Context given by hook
    :return: None
    """

    # Check for valid result and valid state
    global applyFilter
    if ctx.ids is None or not applyFilter:
        applyFilter = False
        return

    applyFilter = False  # reset state

    # Get duplicate ids
    dups = get_dup_ids(ctx.ids)

    # Only keep ids that are in dups variable
    ctx.ids = [i for i in ctx.ids if i in dups]


# Add hooks
browser_will_search.append(check_dups_filter)
browser_did_search.append(filter_result)
