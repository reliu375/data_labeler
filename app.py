import streamlit as st
import pandas as pd
from os.path import join
# https://gist.github.com/okld/0aba4869ba6fdc8d49132e6974e2e662
try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server.Server import Server
except:
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server
from bill_api import *

# Restart the session after labeling a data point.
def trigger_rerun():
    ctx = ReportThread.get_report_ctx()

    this_session = None

    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
                # Streamlit < 0.54.0
                (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
                or
                # Streamlit >= 0.54.0
                (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')
    this_session.request_rerun()

st.title('Labeling Matches between Lobbying Reports and Bills')

try:
    input_data = pd.read_csv('preds.csv')

    filtered_data = input_data[input_data.renbin_label == 2]
    data_item = filtered_data.iloc[0,:]

    st.write('{} of {} items outstanding'.format(filtered_data.shape[0], input_data.shape[0]))

    label = data_item.name

    bill_num, title, short_title = get_bill_info(data_item.loc['bill_id'], data_item.loc['congress_number'])

    if bill_num is None:
        st.write('API request on the bill information has failed. Here is the database info.')
        proposed_bill = st.write('Proposed bill: {}, Congress: {}'.format(data_item.loc['bill_id'], data_item.loc['congress_number']))

    if short_title is None:
        st.write('Short title is not available for this bill')
        st.write('Proposed bill is: {}, of Congress #{}'.format(bill_num, data_item.loc['congress_number']))
        st.write('Full title of this bill: {}'.format(title))
    else:
        st.write('Proposed bill is: {}, of Congress #{}'.format(bill_num, data_item.loc['congress_number']))
        st.write('Full title of this bill: {}'.format(title))
        st.write('Title of this bill: {}'.format(short_title))

    lobby_text = st.write('Issue: {}'.format(data_item.loc['issue_text']))
    bill_subjects = st.write('Bill subjects: {}'.format(data_item.loc['bill_subjects']))

    yes = st.button("Match")
    no = st.button("No Match")

    if yes:
        st.text('aye!')
        input_data.loc[label, 'renbin_label'] = 1
        input_data.to_csv('preds.csv', index=False)
        trigger_rerun()
    if no:
        st.text('nay!')
        input_data.loc[label, 'renbin_label'] = 0
        input_data.to_csv('preds.csv', index=False)
        trigger_rerun()
except IndexError:
    st.error('All labeling done! Congrats!')
