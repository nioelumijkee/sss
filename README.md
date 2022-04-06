pdss - pure data save state
===========================

Еще одна идея сохранения состояния абстракций в ПД.


1. Создать патч. Будем называть его Плагин. В нем могут содержаться любые вещи,
и этот список обьектов будет сохранять состояние:
   +   'tgl' or 'toggle'
   +   'nbx' or 'numberbox'
   +   'vsl' or 'vertical slider'
   +   'hsl' or 'horizontal slider'
   +   'vradio' or 'verical radio'
   +   'hradio' or 'horizontal radio'
   +   'array' with name completion 'ss'
   +   'n_knob'

2. Сохраняем и закрываем патч.

3. В коммандной строке ввести:

		python3 ss.py -i plugin.pd -o plugin_ss.pd

4. Создаем другой патч - Хост, в котором будем использовать патч Плагин.

5. Добавляем один или несколько обьектов Плагин в патч Мастер. Важно, для каждого
обьекта указать уникальный иденктификатор. Это любое число больше 0, в виде первого аргумента
обьекта Плагин. У всех обьектов в патче Мастер должен быть уникальный идентикафиционный номер,
иначе это вызовет ошибку, о чем будет сделано предупреждение в консоли ПД.

6. Добавляем в патч Мастер обьект a_ss.

--------------------------------------------------------------------------------

1. Create pd path('instrument').

2. Add to path several objects. Save state work for this objects:
   +   'tgl' or 'toggle'
   +   'nbx' or 'numberbox'
   +   'vsl' or 'vertical slider'
   +   'hsl' or 'horizontal slider'
   +   'vradio' or 'verical radio'
   +   'hradio' or 'horizontal radio'
   +   'array' with name completion 'ss'
   +   'n_knob'

3. Save and close path.

4. Run: 

        ./toss.py 'file_in.pd' 'file_out.pd'

5. Create another path('master').

6. Add your 'instrument' object this. arguments:
    +   unique number(for every 'ss' object in path)
    +   number of snapshots.

7. Add object 'n_ss' to 'master' path.



Messages for n_ss:
    +   save - for saving state
    +   save_as - for saving as
    +   load - for load state

For local saving (not file) n_ss must be first argument equal 1.

--------------------------------------------------------------------------------

License: GPL v3
Author: Nio
AuthorEmail: nio@dummy.dummy
