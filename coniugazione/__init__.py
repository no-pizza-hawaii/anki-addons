from anki.notes import Note
from aqt import mw, studydeck
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from .fetch import fetch
import requests as re

fields = ['Infinito Presente', 'Indicativo Presente', 'Indicativo Passato prossimo', 'Indicativo Imperfetto',
          'Indicativo Trapassato prossimo', 'Indicativo Passato remoto', 'Indicativo Trapassato remoto',
          'Indicativo Futuro semplice', 'Indicativo Futuro anteriore', 'Condizionale Presente',
          'Condizionale Passato', 'Congiuntivo Presente', 'Congiuntivo Passato', 'Congiuntivo Imperfetto',
          'Congiuntivo Trapassato', 'Imperativo Presente', 'Infinito Passato', 'Participio Presente',
          'Participio Passato', 'Gerundio Presente', 'Gerundio Passato', 'Traduzione']


def add_verb() -> None:
    parent = mw.form.centralwidget
    verb, ok = QInputDialog.getText(parent, 'Enter Verb', 'Verb:')
    if not ok or not verb:
        return

    # Get vocabulary
    try:
        voc = fetch(verb)
    except RuntimeError as ex:
        showInfo(str(ex))
        return
    except re.exceptions.ConnectionError:
        showInfo('Connection Error')
        return
    except Exception as ex:
        showInfo('Unexpected Error: ' + str(ex))
        return

    # Get deck
    # deck = studydeck.StudyDeck(mw, accept='Choose', title='Choose Deck', parent=parent, geomKey='selectDeck')
    # if not deck or not deck.name:
    #     return
    # deck_name = deck.name
    # deck_id = mw.col.decks.by_name(deck_name)['id']
    deck_name = "Verbi irregolari"
    deck_id = mw.col.decks.add_normal_deck_with_name(deck_name).id

    current_notes = mw.col.find_notes(f'"deck:{deck_name}" "note:Coniugazione"')
    for note_id in current_notes:
        note = mw.col.get_note(note_id)
        if note['Infinito Presente'] == voc['Infinito Presente'][0]:
            showInfo(f"'{voc['Infinito Presente'][0]}' already exists in this deck.")
            return

    notetype = mw.col.models.by_name('Coniugazione')
    if notetype is None:  # Create new basic type if note type not yet exists
        # Add new note type
        notetype = mw.col.models.new('Coniugazione')

        # Add note fields and cards
        for name in fields:
            # Add note type field
            field = mw.col.models.new_field(name)
            mw.col.models.add_field(notetype, field)

            # Add note type card
            if name == 'Infinito Presente':
                continue
            t = mw.col.models.new_template(name)
            t['qfmt'] = '{{Infinito Presente}} - ' + name
            t['afmt'] = '{{FrontSide}}\n\n<hr id=answer>\n\n{{' + name + '}}'
            notetype = mw.col.models.add_template(notetype, t)

        # Add note type to collection
        mw.col.models.add(notetype)

    # Set note fields
    note = Note(mw.col, notetype)
    for header in voc:
        lines = voc[header]
        note[header] = '<br/>'.join(lines)

    # Add note to collection
    mw.col.add_note(note, deck_id)
    mw.update()


def suspend_cards() -> None:
    notetype = mw.col.models.by_name("Coniugazione")
    if notetype is None:
        showInfo("Note type unavailable.")
        return
    # templates = {t['name']: t for t in notetype['tmpls']}
    tmpl_indx = {t['name']: i+1 for i, t in enumerate(notetype['tmpls'])}

    default_fields = ['Indicativo Presente', 'Indicativo Imperfetto', 'Condizionale Presente', 'Imperativo Presente',
                      'Infinito Passato', 'Traduzione']

    parent = mw.form.centralwidget
    dialog = QDialog(parent)
    dialog.setWindowTitle("Enable Cards")
    layout = QFormLayout(parent)
    dialog.setLayout(layout)

    boxes = list()
    for name in fields:
        if name == 'Infinito Presente':
            continue

        checkbox = QCheckBox(name, dialog)
        checkbox.setChecked(name in default_fields)
        layout.addWidget(checkbox)
        boxes.append(checkbox)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    qconnect(buttons.accepted, dialog.accept)
    qconnect(buttons.rejected, dialog.reject)
    layout.addWidget(buttons)

    if not dialog.exec():
        return

    for box in boxes:
        name = box.text()
        index = tmpl_indx[name]
        # if box.isChecked() and name not in templates:
        #     t = mw.col.models.new_template(box)
        #     t['qfmt'] = '{{Infinito Presente}} - ' + name
        #     t['afmt'] = '{{FrontSide}}\n\n<hr id=answer>\n\n{{' + name + '}}'
        #     notetype = mw.col.models.add_template(notetype, t)
        # elif not box.isChecked() and name in templates:
        #     t = templates[name]
        #     mw.col.models.remove_template(notetype, t)

        # Suspend unchecked cards instead of deleting the templates
        cards = mw.col.find_cards(f'note:Coniugazione card:{index}')
        if box.isChecked():
            mw.col.sched.unsuspend_cards(cards)
        else:
            mw.col.sched.suspend_cards(cards)

    mw.update()


action1 = QAction('Add Verb Tenses', mw)
action1.setShortcut(QKeySequence("Alt+A"))
qconnect(action1.triggered, add_verb)
mw.form.menuTools.addAction(action1)

action2 = QAction('Suspend Verb Tenses', mw)
qconnect(action2.triggered, suspend_cards)
mw.form.menuTools.addAction(action2)
