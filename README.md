# n_ss - save abstraction state.
### Another one idea for saving abstraction state in Pure Data.

1. Create pd file

2. Add to path several objects. Save state for objects:
   1. 'tgl' or 'toggle'
   2. 'nbx' or 'numberbox'
   3. 'vsl' or 'vertical slider'
   4. 'hsl' or 'horisontal slider'
   5. 'vradio' or 'verical radio'
   6. 'hradio' or 'horisontal radio'

3. Run: 
> ./toss 'path/to/file.pd'
> pd 'path/to/file.pd'

4. Add object 'inlet' and connect to object 'pd ss'.

5. Save pd file.

6. Create another path.

7. Add your object this and added to name object unique digital number. All objects 'ss' must be unique id in path for normal work.

8. Add object 'n_ss'.

9.