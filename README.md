n_ss - save abstraction state.
==============================

Another one idea for saving abstraction state in Pure Data.
-----------------------------------------------------------

1. Create pd file

2. Add to path several objects. Save state work for this objects:
   1. 'tgl' or 'toggle'
   2. 'nbx' or 'numberbox'
   3. 'vsl' or 'vertical slider'
   4. 'hsl' or 'horizontal slider'
   5. 'vradio' or 'verical radio'
   6. 'hradio' or 'horizontal radio'
   7. 'array' with name completion 'ss'

3. Add object 'inlet' and 's $0_ss_snap'. connect them.

4. Add comment with text "snap N" where N - number snaps.

5. Run: 

        ./toss 'file_in.pd' 'file_out.pd'

6. Save pd file.

7. Create another path.

8. Add your object this and added to name object unique digital number. All objects 'ss' must be unique id in path.

9. Add object 'n_ss'.

10. Send messages to n_ss:
    1. Save - for saving state
    2. Save as - for saving as
    3. Load - for load state

