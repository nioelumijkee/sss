n_ss - save abstraction state.
==============================

Another one idea for saving abstraction state in Pure Data.
-----------------------------------------------------------

1. Create pd file

2. Add to path several objects. Save state work for this objects:
   +   'tgl' or 'toggle'
   +   'nbx' or 'numberbox'
   +   'vsl' or 'vertical slider'
   +   'hsl' or 'horizontal slider'
   +   'vradio' or 'verical radio'
   +   'hradio' or 'horizontal radio'
   +   'array' with name completion 'ss'
   +   'n_knob'

3. Add object 'inlet' and 's $0_ss_snap'. connect them.

4. Add comment with text "snap N" where N - number snaps.

5. Run: 

        ./toss 'file_in.pd' 'file_out.pd'

6. Save pd file.

7. Create another path.

8. Add your object this. arguments:
    +   unique number(for every 'ss' object in path)
    +   number of snapshots.

9. Add object 'n_ss'.

10. Send messages to n_ss:
    +   save - for saving state
    +   save_as - for saving as
    +   load - for load state

11. For local saving (not file) n_ss must be first argument equal 1.
