import xlsxwriter
import datetime
from  os import remove
from  os.path import exists
import oracledb
from   util.logger import log
from  db.connect import db_user, db_password, db_dsn
from  app_config import REPORT_PATH

report_name = 'Список зарегистрированых выходов с работы'
report_code = '01'


# stmt = """
#         select event_date, time_out, time_in, employee, post, dep_name, cause, coalesce(head,'Не утверждено'), id 
#         from register r
#         where trunc(event_date,'MM') = trunc(to_date(:mnth,'YYYY-MM-DD'),'MM')
#         order by dep_name, employee, event_date
# """


# active_stmt = stmt

def format_worksheet(worksheet, common_format):
	worksheet.set_row(0, 24)
	worksheet.set_row(1, 24)

	worksheet.set_column(0, 0, 6)
	worksheet.set_column(1, 1, 12)
	worksheet.set_column(2, 2, 12)
	worksheet.set_column(3, 3, 12)
	worksheet.set_column(4, 4, 36)
	worksheet.set_column(5, 5, 36)
	worksheet.set_column(6, 6, 48)
	worksheet.set_column(7, 7, 64)
	worksheet.set_column(8, 8, 36)
	worksheet.set_column(9, 9, 24)

	worksheet.merge_range('A3:A4', '№', common_format)
	worksheet.merge_range('B3:B4', 'Дата регистрации', common_format)
	worksheet.merge_range('C3:C4', 'Время выхода', common_format)
	worksheet.merge_range('D3:D4', 'Время прихода', common_format)
	worksheet.merge_range('E3:E4', 'Сотрудник', common_format)
	worksheet.merge_range('F3:F4', 'Должность', common_format)
	worksheet.merge_range('G3:G4', 'Департамент', common_format)
	worksheet.merge_range('H3:H4', 'Причина отсутствия', common_format)
	worksheet.merge_range('I3:I4', 'ФИО руководителя', common_format)
	worksheet.merge_range('J3:J4', 'Статус', common_format)


def do_report(flt_month: str, file_name: str, active_stmt):
	full_file_name = f'{REPORT_PATH}/{file_name}'
	if exists(file_name):
		remove(file_name)
	with oracledb.connect(user=db_user, password=db_password, dsn=db_dsn) as connection:
		with connection.cursor() as cursor:
			workbook = xlsxwriter.Workbook(full_file_name)

			title_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
			title_format.set_align('vcenter')
			title_format.set_border(1)
			title_format.set_text_wrap()
			title_format.set_bold()

			title_name_report = workbook.add_format({'align': 'left', 'font_color': 'black', 'font_size': '14'})
			title_name_report .set_align('vcenter')
			title_name_report .set_bold()

			common_format = workbook.add_format({'align': 'left', 'font_color': 'black'})
			common_format.set_align('vcenter')
			common_format.set_border(1)

			sum_pay_format = workbook.add_format({'num_format': '#,###,##0.00', 'font_color': 'black', 'align': 'vcenter'})
			sum_pay_format.set_border(1)

			date_format = workbook.add_format({'num_format': 'dd.mm.yyyy', 'align': 'center'})
			date_format.set_border(1)
			date_format.set_align('vcenter')

			date_format_it = workbook.add_format({'num_format': 'dd.mm.yyyy', 'align': 'center'})
			date_format_it.set_align('vcenter')
			date_format_it.set_italic()

			digital_format = workbook.add_format({'num_format': '# ### ##0', 'align': 'center'})
			digital_format.set_border(1)
			digital_format.set_align('vcenter')

			money_format = workbook.add_format({'num_format': '# ### ### ### ##0.00', 'align': 'right'})
			money_format.set_border(1)
			money_format.set_align('vcenter')

			now = datetime.datetime.now()
			log.info(f'Начало формирования {file_name}: {now.strftime("%d-%m-%Y %H:%M:%S")}')
			worksheet = workbook.add_worksheet('Список')
			sql_sheet = workbook.add_worksheet('SQL')
			merge_format = workbook.add_format({
				'bold':     False,
				'border':   6,
				'align':    'left',
				'valign':   'vcenter',
				'fg_color': '#FAFAD7',
				'text_wrap': True
			})
			sql_sheet.merge_range('A1:I35', active_stmt, merge_format)

			worksheet.activate()
			format_worksheet(worksheet=worksheet, common_format=title_format)

			worksheet.write(0, 0, report_name, title_name_report)
			worksheet.write(1, 0, f'За период: {flt_month}', title_name_report)

			row_cnt = 1
			shift_row = 3

			log.info(f'{file_name}. Загружаем данные за период {flt_month}')
			cursor.execute(active_stmt)

			records = cursor.fetchall()
			
			#for record in records:
			for record in records:
				col = 1
				worksheet.write(row_cnt+shift_row, 0, row_cnt, digital_format)
				for list_val in record:
					if col in (1,2,3):
						worksheet.write(row_cnt+shift_row, col, list_val, date_format)
					if col in (4,5,6,7,8):
						worksheet.write(row_cnt+shift_row, col, list_val, common_format)
					if col == 9:
						match list_val:
							case 0:
								worksheet.write(row_cnt+shift_row, col, 'На согласовании', common_format)
							case 1:
								worksheet.write(row_cnt+shift_row, col, 'Согласовано', common_format)
							case 2:
								worksheet.write(row_cnt+shift_row, col, 'Отказано', common_format)
							case _:
								worksheet.write(row_cnt+shift_row, col, f'LIST_VAL: {list_val}', common_format)
					col += 1
				row_cnt += 1
			now = datetime.datetime.now().strftime("%d.%m.%Y (%H:%M:%S)")
			worksheet.write(1, 8, f'Дата формирования: {now}', date_format_it)

			workbook.close()
			now = datetime.datetime.now()
			log.info(f'Формирование отчета {file_name} завершено: {now.strftime("%d-%m-%Y %H:%M:%S")}')
			return full_file_name


if __name__ == "__main__":
    log.debug(f'Отчет {report_code} запускается.')
    do_report('2024-10', 'test.xlsx')
