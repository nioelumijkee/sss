#include "m_pd.h"
#include <stdlib.h>

#define MAX_INS 64
#define MAX_PAR 256
#define MAX_AR 64
#define MAX_BANK 8
#define MAX_SNAP 8
#define ALL_SNAP 64
#define EXT_PRO "pro"
#define EXT_SNAP "snap"
#define NEVER_FOCUS -1

typedef struct _par
{
  int       num;
  t_symbol *type;
  t_symbol *label;
  t_float   min;
  t_float   max;
  t_float   step;
  t_symbol *snd;
  t_symbol *rcv;
  t_float   data[ALL_SNAP];
} t_par;

typedef struct _ar
{
  int       num;
  t_symbol *name;
  t_float  *data[ALL_SNAP];
  int       len[ALL_SNAP];
} t_ar;

typedef struct _ins
{
  int       num;
  t_symbol *name;
  int       localzero;
  int       globalzero;
  t_symbol *path_snap;
  int       sel_bank;
  int       sel_snap;
  char      bank_have_data[MAX_BANK];
  char      snap_have_data[MAX_SNAP];
  char      have_data[ALL_SNAP];
  t_par     par[MAX_PAR];
  int       par_amount;
  t_ar      ar[MAX_AR];
  int       ar_amount;
} t_ins;

static t_class *sss_class;
typedef struct _sss
{
  t_object x_obj;
  /* var */
  int      localzero;
  int      globalzero;
  int      focus;
  /* names */
  t_symbol *abs_name;
  t_symbol *pro_name;
  /* path */
  t_symbol *path_sss;
  t_symbol *path_allpro;
  t_symbol *path_allsnap;
  t_symbol *path_pro;
  /* send names global */
  t_symbol *s_get_info;
  t_symbol *s_focus;
  /* send names local */
  t_symbol *s_path_pro;
  t_symbol *s_path_snap;
  t_symbol *s_cnv_abs_name;
  t_symbol *s_cnv_pro_name;
  t_symbol *s_cnv_ins_name;
  t_symbol *s_sel_bank;
  t_symbol *s_bank_have_data;
  t_symbol *s_sel_snap;
  t_symbol *s_snap_have_data;
  /* ins */
  t_ins    ins[MAX_INS];
  int      ins_amount;
} t_sss;

t_symbol *s_empty;

void sss_init(t_sss *x)
{
  /* var */
  x->focus = NEVER_FOCUS;
  /* names */
  x->abs_name = s_empty;
  x->pro_name = s_empty;
  /* path */
  x->path_sss = s_empty;
  x->path_allpro = s_empty;
  x->path_allsnap = s_empty;
  x->path_pro = s_empty;
  /* send names global */
  x->s_get_info = s_empty;
  x->s_focus = s_empty;
  /* send names local */
  x->s_path_pro = s_empty;
  x->s_path_snap = s_empty;
  x->s_cnv_abs_name = s_empty;
  x->s_cnv_pro_name = s_empty;
  x->s_cnv_ins_name = s_empty;
  x->s_sel_bank = s_empty;
  x->s_bank_have_data = s_empty;
  x->s_sel_snap = s_empty;
  x->s_snap_have_data = s_empty;
  /* ins */
  for (int i=0; i<x->ins_amount; i++)
    {
      x->ins[i].num = -1;
      x->ins[i].name = s_empty;
      x->ins[i].localzero = 0;
      x->ins[i].globalzero = 0;
      x->ins[i].path_snap = s_empty;
      x->ins[i].sel_bank = 0;
      x->ins[i].sel_snap = 0;
      for (int j=0; j<MAX_BANK; j++)
	x->ins[i].bank_have_data[j] = 0;
      for (int j=0; j<MAX_SNAP; j++)
	x->ins[i].snap_have_data[j] = 0;
      for (int j=0; j<ALL_SNAP; j++)
	x->ins[i].have_data[j] = 0;
      /* par */
      for (int j=0; j<MAX_PAR; j++)
	{
	  x->ins[i].par[j].num = 0;
	  x->ins[i].par[j].type = s_empty;
	  x->ins[i].par[j].label = s_empty;
	  x->ins[i].par[j].min = 0.0;
	  x->ins[i].par[j].max = 0.0;
	  x->ins[i].par[j].step = 0.0;
	  x->ins[i].par[j].snd = s_empty;
	  x->ins[i].par[j].rcv = s_empty;
	  for (int k=0; k<ALL_SNAP; k++)
	    x->ins[i].par[j].data[k] = 0.0;
	}
      x->ins[i].par_amount = 0;
      /* ar */
      for (int j=0; j<MAX_AR; j++)
	{
	  x->ins[i].ar[j].num = 0;
	  x->ins[i].ar[j].name = s_empty;
	  for (int k=0; k<ALL_SNAP; k++)
	    {
	      if (x->ins[i].ar[j].data[k] != NULL)
		{
		  free(x->ins[i].ar[j].data[k]);
		  x->ins[i].ar[j].data[k] = NULL;
		}
	      x->ins[i].ar[j].len[k] = 0;
	    }
	}
      x->ins[i].ar_amount = 0;
    }
}

void *sss_new(t_symbol *s, int ac, t_atom *av)
{
  t_sss *x = (t_sss *)pd_new(sss_class);
  outlet_new(&x->x_obj, 0);
  sss_init(x);
  x->localzero = atom_getfloatarg(0, ac, av);
  x->globalzero = atom_getfloatarg(1, ac, av);
  return (void *)x;
  if(s){}; // nouse
}

void sss_setup(void)
{
  sss_class = class_new(gensym("sss"),
			   (t_newmethod)sss_new,
			   0,
			   sizeof(t_sss),
			   0, A_GIMME, 0);
  class_addmethod(sss_class,(t_method)sss_init,gensym("init"),0);
  s_empty = gensym("");
}
