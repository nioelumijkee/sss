/* snapshot browser */

/*

structure snap array:
[0 ... 3] snap
[] amount snap
[] table snap starts
[] snaps

structure snap:
[0 ... 15] name
[16 ...] data

*/



#include <string.h>
#include "m_pd.h"

#define DEBUG(X) X
#define MAX_SNAPS 128
#define SNAPS_START 13
#define MAX_NAME 16
#define MAX_NAME_1 17


//----------------------------------------------------------------------------//
// clip min max
#define AF_CLIP_MINMAX(MIN, MAX, IN) \
  if ((IN) < (MIN))		     \
    (IN) = (MIN);		     \
  else if ((IN) > (MAX))	     \
    (IN) = (MAX);

//----------------------------------------------------------------------------//
// clip min
#define AF_CLIP_MIN(MIN, IN) \
  if ((IN) < (MIN))	     \
    (IN) = (MIN);

//----------------------------------------------------------------------------//
// clip max
#define AF_CLIP_MAX(MAX, IN) \
  if ((IN) > (MAX))	     \
    (IN) = (MAX);



static t_class *n_snapshot_class;

typedef struct _n_snapshot
{
  t_object x_obj;
  t_outlet *out;
  int fs; /* settings */
  int width;
  int height;
  int fdx;
  int fdy;
  int rows;
  int columns;
  int rect_fcol_na;
  int rect_bcol_na;
  int text_col_na;
  int rect_fcol_a;
  int rect_bcol_a;
  int text_col_a;
  int c_w;
  int c_h;
  int l_a; /* array */
  t_symbol *s_a;
  t_word *w_a;
  t_garray *g_a;
  int amount_snap; /* snap array */
  short int offset; /* scroll */
  short int cursor;
  short int scroll_clip;
  short int scroll_max;
  char snap_names[MAX_SNAPS][MAX_NAME_1]; /* names */
} t_n_snapshot;

//----------------------------------------------------------------------------//
void n_snapshot_init_canvas(t_n_snapshot *x)
{
  int i;
  t_atom a[10];
  x->c_w = x->width;
  x->c_h = x->height * x->rows;

  // size
  SETSYMBOL(a, gensym("size"));
  SETFLOAT(a + 1, (t_float)x->c_w);
  SETFLOAT(a + 2, (t_float)x->c_h);
  outlet_anything(x->out, gensym("cnv"), 3, a);

  // maxel
  SETSYMBOL(a, gensym("maxel"));
  SETFLOAT(a + 1, (t_float)x->rows * 2);
  outlet_anything(x->out, gensym("cnv"), 2, a);

  // rect
  for (i=0; i < x->rows; i++)
    {
      SETFLOAT(a, (t_float) 3);
      SETFLOAT(a + 1, (t_float) i);
      SETFLOAT(a + 2, (t_float) x->rect_fcol_na);
      SETFLOAT(a + 3, (t_float) x->rect_bcol_na);
      SETFLOAT(a + 4, (t_float) 1); // width
      SETFLOAT(a + 5, (t_float) 0); // x0
      SETFLOAT(a + 6, (t_float) i * x->height); // y0
      SETFLOAT(a + 7, (t_float) x->width); // x1
      SETFLOAT(a + 8, (t_float) (i + 1) * x->height); // y1
      outlet_anything(x->out, gensym("cnv"), 9, a);
    }

  // text
  for (i=0; i < x->rows; i++)
    {
      SETFLOAT(a, (t_float) 8);
      SETFLOAT(a + 1, (t_float) i + x->rows);
      SETFLOAT(a + 2, (t_float) x->text_col_na);
      SETFLOAT(a + 3, (t_float) x->fs);
      SETFLOAT(a + 4, (t_float) x->fdx); // x0
      SETFLOAT(a + 5, (t_float) (i * x->height) + x->fdy); // y0
      SETSYMBOL(a + 6, gensym("[...][................]")); // text
      outlet_anything(x->out, gensym("cnv"), 7, a);
    }
}

//----------------------------------------------------------------------------//
void n_snapshot_display_canvas(t_n_snapshot *x)
{
  int i,j;
  t_atom a[10];
  char buf[32];

  // rect
  for (i=0; i < x->rows; i++)
    {
      SETFLOAT(a, (t_float) 10); // color
      SETFLOAT(a + 1, (t_float) i); // id

      j = i + x->offset;


      if (j == x->cursor)
	{
	  SETFLOAT(a + 2, (t_float) x->rect_fcol_a);
	  SETFLOAT(a + 3, (t_float) x->rect_bcol_a);
	}
      else
	{
	  SETFLOAT(a + 2, (t_float) x->rect_fcol_na);
	  SETFLOAT(a + 3, (t_float) x->rect_bcol_na);
	}

      outlet_anything(x->out, gensym("cnv"), 4, a);
    }

  // text color
  for (i=0; i < x->rows; i++)
    {
      SETFLOAT(a, (t_float) 10); // color
      SETFLOAT(a + 1, (t_float) i + x->rows); // id

      j = i + x->offset;

      if (j == x->cursor)
	{
	  SETFLOAT(a + 2, (t_float) x->text_col_a);
	}
      else
	{
	  SETFLOAT(a + 2, (t_float) x->text_col_na);
	}

      outlet_anything(x->out, gensym("cnv"), 3, a);
    }

  // text text
  for (i=0; i < x->rows; i++)
    {
      SETFLOAT(a, (t_float) 13); // text
      SETFLOAT(a + 1, (t_float) i + x->rows); // id

      j = i + x->offset;

      sprintf(buf, "[%3d][%s]",j, x->snap_names[j]);
      SETSYMBOL(a + 2, gensym(buf));
      outlet_anything(x->out, gensym("cnv"), 3, a);
    }
  post("offset: %d",x->offset);
  post("cursor: %d",x->cursor);
}

//----------------------------------------------------------------------------//
void n_snapshot_scroll_f(t_n_snapshot *x, t_floatarg f)
{
  if      (f < 0) f = 0;
  else if (f > 1) f = 1;
  x->offset = f * x->scroll_max; 
  n_snapshot_display_canvas(x);
}

//----------------------------------------------------------------------------//
void n_snapshot_scroll_up(t_n_snapshot *x, t_floatarg f)
{
  int i; 
  t_atom a[2];
  for (i = 0; i < f; i++)
    {
      // one step
      x->cursor--;
      AF_CLIP_MIN(0, x->cursor);

      // offset
      if (x->cursor < (x->offset + 1))
	x->offset = x->cursor;

      // offset
      if (x->cursor > (x->offset + x->rows))
	x->offset = x->cursor - x->rows + 1;
    }

  n_snapshot_display_canvas(x);

  // sl
  SETFLOAT(a, (t_float)x->offset / (MAX_SNAPS - x->rows));
  outlet_anything(x->out, gensym("sl"), 1, a);
}

//----------------------------------------------------------------------------//
void n_snapshot_scroll_down(t_n_snapshot *x, t_floatarg f)
{
  int i;
  t_atom a[2];
  for (i = 0; i < f; i++)
    {
      // one step
      x->cursor++;
      if (x->cursor >= MAX_SNAPS)
	x->cursor = MAX_SNAPS - 1;

      // offset down
      if (x->cursor >= (x->offset + x->rows))
	x->offset = x->cursor - x->rows + 1;

      // offset
      if (x->cursor < x->offset)
	x->offset = x->cursor;

      AF_CLIP_MAX(x->scroll_max, x->offset);
    }

  n_snapshot_display_canvas(x);

  // sl
  SETFLOAT(a, (t_float)x->offset / (MAX_SNAPS - x->rows));
  outlet_anything(x->out, gensym("sl"), 1, a);
}

//----------------------------------------------------------------------------//
int pd_open_array(t_symbol *s_arr, // name
		  t_word **w_arr,  // word
		  t_garray **g_arr) // garray
{
  int len;
  t_word *i_w_arr;
  t_garray *i_g_arr;
  if (!(i_g_arr = (t_garray *)pd_findbyclass(s_arr, garray_class)))
    {
      error("%s: no such array", s_arr->s_name);
      len = -1;
    }
  else if (!garray_getfloatwords(i_g_arr, &len, &i_w_arr))
    {
      error("%s: bad template", s_arr->s_name);
      len = -1;
    }
  else
    {
      *w_arr = i_w_arr;
      *g_arr = i_g_arr;
    }
  return (len);
}

//----------------------------------------------------------------------------//
int n_snapshot_validate_snaparray(t_n_snapshot *x)
{
  int i,j,k,l;

  // snap
  if (x->w_a[0].w_float != (t_float)'s' ||
      x->w_a[1].w_float != (t_float)'n' ||
      x->w_a[2].w_float != (t_float)'a' ||
      x->w_a[3].w_float != (t_float)'p')
    {
      post("n_snapshot error: \'snap\' in array");
      return(1);
    }
  
  // amount snap
  if (x->w_a[4].w_float < 0 || 
      x->w_a[4].w_float > MAX_SNAPS)
    {
      post("n_snapshot error: amount snap in array");
      return(1);
    }
  else
    {
      x->amount_snap = x->w_a[4].w_float;
    }
  
  // table snaps start
  for (i=0; i < x->amount_snap; i++)
    {
      j = i + 5;
      if (j < x->l_a)
	{
	  if (x->w_a[j].w_float >= x->l_a || 
	      x->w_a[j].w_float < SNAPS_START)
	    {
	      post("n_snapshot error: snap starts [%d] is not range: %d [%d ... %d]",
		   i,
		   (int)x->w_a[j].w_float,
		   SNAPS_START,
		   x->l_a - 1);
	      return(1);
	    }

	  // copy name
	  l = x->w_a[j].w_float;
	  for (k=0; k < MAX_NAME; k++)
	    {
	      x->snap_names[i][k] = (char)x->w_a[l].w_float;
	      l++;
	      if (l >= x->l_a)
		{
		  post("n_snapshot error: snap [%d] is bad name: %d [%d ... %d]",
		       i,
		       l,
		       SNAPS_START,
		       x->l_a - 1);
		  return(1);
		}
	    }
	  x->snap_names[i][MAX_NAME] = '\0';
	}
      else
	{
	  post("n_snapshot error: table snap starts");
	  return(1);
	}
    }
  return(0);
}

//----------------------------------------------------------------------------//
int n_snapshot_init_snaparray(t_n_snapshot *x)
{
  int i;
  garray_resize(x->g_a, SNAPS_START);
  x->l_a = pd_open_array(x->s_a, &x->w_a, &x->g_a);
  x->w_a[0].w_float = (t_float)'s';
  x->w_a[1].w_float = (t_float)'n';
  x->w_a[2].w_float = (t_float)'a';
  x->w_a[3].w_float = (t_float)'p';
  for (i = 4; i < x->l_a; i++)
    {
      x->w_a[i].w_float = 0.0;
    }
  x->amount_snap = 0;
  garray_redraw(x->g_a);

  for (i = 0; i < MAX_SNAPS; i++)
    {
      sprintf(x->snap_names[i],"..........");
    }
}

//----------------------------------------------------------------------------//
void n_snapshot_init(t_n_snapshot *x, t_symbol *s)
{
  t_atom a[2];

  // canvas
  n_snapshot_init_canvas(x); // < -remove this
  
  // array
  x->s_a = s;
  x->l_a = pd_open_array(x->s_a, &x->w_a, &x->g_a);
  if (n_snapshot_validate_snaparray(x))
    {
      post("n_snapshot error: validate array");
      n_snapshot_init_snaparray(x);
    }


  x->scroll_max = MAX_SNAPS - x->rows;
  AF_CLIP_MIN(0, x->scroll_max);
  x->scroll_clip = MAX_SNAPS - 1;
  AF_CLIP_MAX(x->rows - 1, x->scroll_clip);

  x->offset = 0;
  x->cursor = 0;

  // sl
  SETFLOAT(a, (t_float)0);
  outlet_anything(x->out, gensym("sl"), 1, a);
}

//----------------------------------------------------------------------------//
void n_snapshot_cnv(t_n_snapshot *x, t_floatarg m, t_floatarg mx, t_floatarg my, t_floatarg mod1, t_floatarg mod2)
{
  t_atom a[2];
  int pos_y;
  if (m == 1)
    {
      pos_y = my / x->height;
      if      (pos_y < 0)         pos_y = 0;
      else if (pos_y > x->rows-1) pos_y = x->rows-1;
      
      // out
      SETFLOAT(a, (t_float)pos_y);
      outlet_anything(x->out, gensym("snap"), 1, a);

      // mod
      if (mod1 == 1)
	{
	  // out
	  SETFLOAT(a, (t_float)1);
	  outlet_anything(x->out, gensym("snap_act1"), 1, a);
	}

      // mod
      else if (mod2 == 1)
	{
	  // out
	  SETFLOAT(a, (t_float)1);
	  outlet_anything(x->out, gensym("snap_act2"), 1, a);
	}

      // cursor
      x->cursor = x->offset + pos_y;
      n_snapshot_display_canvas(x);
    }
}

//----------------------------------------------------------------------------//
void n_snapshot_add(t_n_snapshot *x)
{
}

//----------------------------------------------------------------------------//
void n_snapshot_erase(t_n_snapshot *x)
{
}

//----------------------------------------------------------------------------//
void n_snapshot_store(t_n_snapshot *x)
{
}

//----------------------------------------------------------------------------//
void *n_snapshot_new(t_symbol *s, int ac, t_atom *av)
{
  t_n_snapshot *x = (t_n_snapshot *)pd_new(n_snapshot_class);

  x->fs = 11;
  x->width = 160;
  x->height = 20;
  x->fdx = 4;
  x->fdy = 4;
  x->rows = 16;
  x->columns = 16;
  x->rect_fcol_na = 22;
  x->rect_bcol_na = 0;
  x->text_col_na = 22;
  x->rect_fcol_a = 13;
  x->rect_bcol_a = 3;
  x->text_col_a = 19;

  // arguments
  if (ac >= 1)  x->fs            = atom_getfloatarg(0, ac, av);
  if (ac >= 2)  x->width         = atom_getfloatarg(1, ac, av);
  if (ac >= 3)  x->height        = atom_getfloatarg(2, ac, av);
  if (ac >= 4)  x->fdx           = atom_getfloatarg(3, ac, av);
  if (ac >= 5)  x->fdy           = atom_getfloatarg(4, ac, av);
  if (ac >= 6)  x->rows          = atom_getfloatarg(5, ac, av);
  if (ac >= 7)  x->columns       = atom_getfloatarg(6, ac, av);
  if (ac >= 8)  x->rect_fcol_na  = atom_getfloatarg(7, ac, av);
  if (ac >= 9)  x->rect_bcol_na  = atom_getfloatarg(8, ac, av);
  if (ac >= 10) x->text_col_na   = atom_getfloatarg(9, ac, av);
  if (ac >= 11) x->rect_fcol_a   = atom_getfloatarg(10, ac, av);
  if (ac >= 12) x->rect_bcol_a   = atom_getfloatarg(11, ac, av);
  if (ac >= 13) x->text_col_a    = atom_getfloatarg(12, ac, av);

  DEBUG(post("fs            = %d", x->fs));
  DEBUG(post("width         = %d", x->width));
  DEBUG(post("height        = %d", x->height));
  DEBUG(post("fdx           = %d", x->fdx));
  DEBUG(post("fdy           = %d", x->fdy));
  DEBUG(post("rows          = %d", x->rows));
  DEBUG(post("columns       = %d", x->columns));
  DEBUG(post("rect_fcol_na  = %d", x->rect_fcol_na));
  DEBUG(post("rect_bcol_na  = %d", x->rect_bcol_na));
  DEBUG(post("text_col_na   = %d", x->text_col_na));
  DEBUG(post("rect_fcol_a   = %d", x->rect_fcol_a));
  DEBUG(post("rect_bcol_a   = %d", x->rect_bcol_a));
  DEBUG(post("text_col_a    = %d", x->text_col_a));
  
  x->out = outlet_new(&x->x_obj, 0);
  
  return (void *)x;
}

//----------------------------------------------------------------------------//
void n_snapshot_setup(void)
{
  n_snapshot_class = class_new(gensym("n_snapshot"), (t_newmethod)n_snapshot_new, NULL, sizeof(t_n_snapshot), CLASS_DEFAULT, A_GIMME, 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_init, gensym("init"), A_SYMBOL, 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_cnv, gensym("cnv"), A_DEFFLOAT, A_DEFFLOAT, A_DEFFLOAT, A_DEFFLOAT, A_DEFFLOAT, 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_scroll_f, gensym("scroll_f"), A_DEFFLOAT, 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_scroll_up, gensym("scroll_up"), A_DEFFLOAT, 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_scroll_down, gensym("scroll_down"), A_DEFFLOAT, 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_add, gensym("add"), 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_erase, gensym("erase"), 0);
  class_addmethod(n_snapshot_class, (t_method)n_snapshot_store, gensym("store"), 0);
}
