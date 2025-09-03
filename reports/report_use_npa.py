from configparser import ConfigParser
import xlsxwriter
import datetime
from   util.logger import log
import oracledb
import os.path
from  app_config import REPORT_PATH

from reports.list_npa import list_npa


report_name = 'Сведения о количестве обращений к НПА'
report_code = 'UNPA'


def get_select():
	pivot_columns = ',\n    '.join(
		f"'{el['name']}' AS \"{el['name']}\"" for el in list_npa
	)
	stmt_report = f"""
		select * 
		from (
			select dep_name, user_name, file_name
			from use_doc
			where extract(year from date_op)=:year
		)
		pivot(
			count(file_name)
			for file_name in (
				{pivot_columns}
			)
		)
		order by dep_name, user_name
	"""
	log.debug(f"SQL: {stmt_report}")

	return stmt_report


def format_worksheet(worksheet, common_format):
	worksheet.set_row(0, 24)
	worksheet.set_row(1, 24)

	worksheet.set_column(0, 0, 5)
	worksheet.set_column(1, 1, 44)
	worksheet.set_column(2, 2, 32)

	worksheet.write(2, 0, '№', common_format)
	worksheet.write(2, 1, 'Департамент', common_format)
	worksheet.write(2, 2, 'Сотрудник', common_format)

	step = 1
	first_col = 3
	for num_col in range(1, len(list_npa)+1):
		worksheet.set_column((num_col-1)*step + first_col, (num_col-1)*step + first_col, 32)
		worksheet.write(2,(num_col-1)*step + first_col, list_npa[num_col-1]['name'], common_format)
	

def report_use_npa(year):
	file_name = f'{REPORT_PATH}/USE_NPA_{year}.xlsx'
	if os.path.isfile(file_name):
		os.remove(file_name)
		log.info(f'Отчет уже существует {file_name}')

	s_date = datetime.datetime.now().strftime("%H:%M:%S")

	log.info(f'DO REPORT. START CREATE {file_name}')

	config = ConfigParser()
	config.read('db_config.ini')
	
	ora_config = config['db_60']
	db_user=ora_config['db_user']
	db_password=ora_config['db_password']
	db_dsn=ora_config['db_dsn']
	log.info(f'{report_code}. db_user: {db_user}, db_dsn: {db_dsn}')
	
	with oracledb.connect(user=db_user, password=db_password, dsn=db_dsn) as connection:
		with connection.cursor() as cursor:
			workbook = xlsxwriter.Workbook(file_name)

			title_format = workbook.add_format({'bg_color': '#D1FFFF', 'align': 'center', 'font_color': 'black'})
			#title_format = workbook.add_format({'bg_color': '#C5FFFF', 'align': 'center', 'font_color': 'black'})
			title_format.set_align('vcenter')
			title_format.set_border(1)
			title_format.set_text_wrap()
			title_format.set_bold()

			title_name_report = workbook.add_format({'align': 'left', 'font_color': 'black', 'font_size': '14'})
			title_name_report .set_align('vcenter')
			title_name_report .set_bold()

			title_format_it = workbook.add_format({'align': 'right'})
			title_format_it.set_align('vcenter')
			title_format_it.set_italic()

			title_report_code = workbook.add_format({'align': 'right', 'font_size': '14'})
			title_report_code.set_align('vcenter')
			title_report_code.set_bold()

			common_format = workbook.add_format({'align': 'center', 'font_color': 'black'})
			common_format.set_align('vcenter')
			common_format.set_border(1)

			region_name_format = workbook.add_format({'align': 'left', 'font_color': 'black'})
			region_name_format.set_align('vcenter')
			region_name_format.set_border(1)

			category_name_format = workbook.add_format({'align': 'center', 'font_color': 'black'})
			category_name_format.set_align('vcenter')
			category_name_format.set_border(1)

			category_name_format_1 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_1.set_border(1)
			category_name_format_1.set_bg_color('#FFF8DC')	  # Желтенький
			category_name_format_2 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_2.set_bg_color('#DAFBC5')	  # Зелененький
			category_name_format_3 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_3.set_bg_color('#FDFEE5')	  # Желтенький
			category_name_format_4 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_4.set_bg_color('#EBE6FF')	  #  Светло-голубой
			category_name_format_5 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_5.set_bg_color('#FFFFE0')	  # Слегка желтенький
			category_name_format_6 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_6.set_bg_color('#FFE1E1')	  # Розовый
			category_name_format_7 = workbook.add_format({'align': 'left', 'font_color': 'black'})
			category_name_format_7.set_bg_color('#E0F7FF')    # Голубой
			category_name_format_1.set_border(1)
			category_name_format_2.set_border(1)
			category_name_format_3.set_border(1)
			category_name_format_4.set_border(1)
			category_name_format_5.set_border(1)
			category_name_format_6.set_border(1)
			category_name_format_7.set_border(1)

			sum_pay_format = workbook.add_format({'num_format': '#,###,##0.00', 'font_color': 'black', 'align': 'vcenter'})
			sum_pay_format.set_border(1)

			date_format = workbook.add_format({'num_format': 'dd.mm.yyyy', 'align': 'center'})
			date_format.set_border(1)
			date_format.set_align('vcenter')

			number_format = workbook.add_format({'num_format': '# ### ### ##0', 'align': 'center'})
			number_format.set_border(1)
			number_format.set_align('vcenter')

			digital_format = workbook.add_format({'num_format': '# ### ### ##0', 'align': 'center'})
			digital_format.set_border(1)
			digital_format.set_align('vcenter')

			money_format = workbook.add_format({'num_format': '### ### ### ### ##0.00', 'align': 'right'})
			money_format.set_border(1)
			money_format.set_align('vcenter')

			percent_format = workbook.add_format({'num_format': '### ##0.00', 'align': 'center'})
			percent_format.set_border(1)
			percent_format.set_align('vcenter')

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
			stmt_report = get_select()

			sql_sheet.merge_range('A1:I25', f'{stmt_report}', merge_format)

			worksheet.activate()
			format_worksheet(worksheet=worksheet, common_format=title_format)

			worksheet.write(0, 0, report_name, title_name_report)
			worksheet.write(1, 0, f'За период: {year}', title_name_report)

			cursor = connection.cursor()
			log.info(f'{file_name}. Загружаем данные за период {year}')
			
			try:
				cursor.execute(stmt_report, year=year)
			except oracledb.DatabaseError as e:
				error, = e.args
				log.error(f"ERROR. REPORT {report_code}. error_code: {error.code}, error: {error.message}\n{stmt_report}")
				return
			finally:
				log.info(f'REPORT: {report_code}. Выборка из курсора завершена')

			log.info(f'REPORT: {report_code}. Формируем выходную EXCEL таблицу')

			records = []
			records = cursor.fetchall()
			row_cnt = 1
			shift_row = 2
			#for record in records:
			for record in records:
				col = 0
				worksheet.write(row_cnt+shift_row, col, row_cnt, digital_format)
				for list_val in record:
					col += 1
					if col in (1,2):
						worksheet.write(row_cnt+shift_row, col, list_val, region_name_format)
					else:
						worksheet.write(row_cnt+shift_row, col, list_val, digital_format)
				row_cnt += 1

			# Шифр отчета
			worksheet.write(0, 6, report_code, title_report_code)
			
			now = datetime.datetime.now()
			stop_time = now.strftime("%H:%M:%S")

			worksheet.write(1, 6, f'Дата формирования: {now.strftime("%d.%m.%Y ")}({s_date} - {stop_time})', title_format_it)
			#
			workbook.close()
			log.info(f'REPORT: {report_code}. Формирование отчета {file_name} завершено ({s_date} - {stop_time}). Строк в отчете: {row_cnt-1}')
			return file_name
