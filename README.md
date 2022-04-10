## pdss - pure data save state

--------------------------------------------------------------------------------

Еще одна идея сохранения состояния абстракций в ПД.


1. Создать патч. Будем называть его Плагин. В нем могут содержаться любые вещи,
и этот список обьектов будет сохранять состояние:
   + 'tgl' or 'toggle'.
   + 'nbx' or 'numberbox'.
   + 'vsl' or 'vertical slider'.
   + 'hsl' or 'horizontal slider'.
   + 'vradio' or 'verical radio'.
   + 'hradio' or 'horizontal radio'.
   + 'array' with word 'pdss' in name.
   + 'n_knob'.

2. Сохраняем и закрываем патч.

3. В коммандной строке ввести:

		python3 pdss.py -f plugin.pd -o plugin_ss.pd

4. Создаем другой патч - Хост, в котором будем использовать патч Плагин.

5. Добавляем один или несколько обьектов Плагин в патч Мастер. Важно, для каждого
обьекта указать уникальный иденктификатор. Это любое число больше 0, в виде первого аргумента
обьекта Плагин. У всех обьектов в патче Мастер должен быть уникальный идентикафиционный номер,
иначе это вызовет ошибку, о чем будет сделано предупреждение в консоли ПД.

6. Добавляем в патч Мастер обьект a_ss.

--------------------------------------------------------------------------------

### a_pdss

arguments:
	+ when 1 local saving to 'savestate' activated.

inlet:
	+ open <filename>
	  + open file.
	  + copy file to main buffer.
	  + set filename.
	  + from main buffer copy to all instruments.
	+ save
	  + from all instruments copy all arrays to main buffer.
	  + save main buffer to object 'savestate'.
	  + if filename is set, save main buffer to file.
	+ save_as <filename>
	  + from all instruments copy all arrays to main buffer.
	  + save main buffer to object 'savestate'.
	  + set filename.
	  + save main buffer to file.

outlet:
	+ info

init when load:
	+ copy from object savestate to main buffer
	+ set filename 'empty'.
	+ from main buffer copy to all instruments.


### a_pdss-driver

No commands.

### a_pdss-par

No commands.

### a_pdss-array

No commands.

--------------------------------------------------------------------------------

### structure saved files

header main:
	+ [0] size file
	+ [1] amount arrays
table arrays:
	+ [0] id ins
	+ [1] number array
	+ [2] size array
data:
	+ data

--------------------------------------------------------------------------------

### pdss.py

Python script for automatisation.
