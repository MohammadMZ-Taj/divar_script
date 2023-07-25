from db_model import Record
from db_crud import *

record_data = ['secrettoken', 'title', 'topdesc', 'middledesc', 'bottomdesc', 1, 'google.com', 'land area', 'area', 2000]
#
# record_obj = save_record(*record_data, is_sent=True)
update_record(record_data[0], sent_status=False)
# r = session.query(Record).filter(Record.token == 'secrettoken').all()[0]
# print(r)
# print(r.is_sent)
# r.is_sent = True
# session.commit()
# print(r.is_sent)
# print(record_obj.is_sent)
