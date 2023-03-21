#include "m_pd.h"
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h> // stat
#include <dirent.h>   // DIR opendir
#include <unistd.h> // access

////////////////////////////////////////////////////////////////////////////////
#define MAX_STRING 512
#define MAX_INS 64
#define MAX_PAR 256
#define MAX_AR 64
#define MAX_SNAP 32
#define MAX_ABS_NAME 128
#define ENV_PD_SSS "PD_SSS"
#define E_NO 0
#define E_YES 1
#define E_OK 0
#define E_ERR 1
#define NOUSE(X) if(X){};
#define DEFAULT_PRO_NAME "default"

////////////////////////////////////////////////////////////////////////////////
typedef struct _par
{
  int       ex;
  t_symbol *type;
  t_symbol *label;
  t_float   min;
  t_float   max;
  t_float   step;
  t_symbol *snd;
  t_symbol *rcv;
  t_float   data[MAX_SNAP];
} t_par;

typedef struct _ar
{
  int       ex;
  t_symbol *name;
  t_float  *data[MAX_SNAP];
  int       len[MAX_SNAP];
} t_ar;

typedef struct _ins
{
  int       ex;
  t_symbol *name;
  int       localzero;
  int       globalzero;
  t_symbol *path_snap;
  int       sel_snap;
  char      have_data[MAX_SNAP];
  t_par     par[MAX_PAR];
  t_ar      ar[MAX_AR];
} t_ins;

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
  t_symbol *s_focus;
  /* send names local */
  t_symbol *s_path_pro;
  t_symbol *s_path_snap;
  t_symbol *s_cnv_abs_name;
  t_symbol *s_cnv_pro_name;
  t_symbol *s_cnv_ins_name;
  t_symbol *s_sel_snap;
  t_symbol *s_have_data;
  /* ins */
  t_ins    ins[MAX_INS];
  /* buf */
  t_float  buf_par[MAX_PAR];
  t_float *buf_ar[MAX_AR];
  int      buf_ar_l[MAX_AR];
} t_sss;

////////////////////////////////////////////////////////////////////////////////
static t_class *sss_class;
t_symbol *s_empty;
t_symbol *s_label;

////////////////////////////////////////////////////////////////////////////////
// create dir
int exorcr_dir(t_symbol *p)
{
  int err;
  struct stat st;
  err = stat(p->s_name, &st);
  if (err != 0)
    {
      // create
      err = mkdir(p->s_name, S_IRWXU);
      if (err != 0)
	{
	  post("error: mkdir or stat: %s", p->s_name);
	  return (E_ERR);
	}
      else
	{
	  post("mkdir: %s", p->s_name);
	  err = stat(p->s_name, &st);
	}
    }
  if (!S_ISDIR(st.st_mode)) 
    {
      post("error: not dir: %s", p->s_name);
      return (E_ERR);
    }
  // access
  if (access(p->s_name, R_OK|W_OK|X_OK) < 0) 
    {
      post("error: access to: %s", p->s_name);
      return (E_ERR);
    }
  return (E_OK);
}

// get par value
t_float get_par(t_symbol *n)
{
  t_float *x_floatstar;
  x_floatstar = value_get(n);
  return(*x_floatstar);
}

// set par value
void set_par(t_symbol *n, t_float f)
{
  if (n->s_thing) { pd_float(n->s_thing, f); }
}

// save snap to file
void save_snap_to_file(t_ins *ins, int n, const char *filename)
{
  int size=0;
  float buf[MAX_PAR];
  FILE *fd;
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  buf[size] = ins->par[j].data[n];
	  size++;
	}
    }
  fd = fopen(filename, "wb");
  if (fd == NULL)
    {
      post("error: open file: %s", filename);
      return;
    }
  fwrite(buf, sizeof(float), size, fd);
  fclose(fd);
}

// open and read file to array snap
void open_file_to_snap(t_ins *ins, int n, const char *filename)
{
  int size=0;
  float buf;
  FILE *fd;
  fd = fopen(filename, "rb");
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  fread(&buf, sizeof(float), 1, fd);
	  ins->par[j].data[n] = (t_float)buf;
	  size++;
	}
    }
  fclose(fd);
}

////////////////////////////////////////////////////////////////////////////////
void sss_init(t_sss *x)
{
  char buf[MAX_STRING];
  /* var */
  x->focus = 0;
  /* names */
  x->pro_name = gensym(DEFAULT_PRO_NAME);
  /* send names global */
  sprintf(buf, "%d-sss-focus", x->globalzero);          x->s_focus = gensym(buf);
  /* send names local */
  sprintf(buf, "%d-sss-path-pro", x->localzero);        x->s_path_pro = gensym(buf);
  sprintf(buf, "%d-sss-path-snap", x->localzero);       x->s_path_snap = gensym(buf);
  sprintf(buf, "%d-sss-cnv-abs-name", x->localzero);    x->s_cnv_abs_name = gensym(buf);
  sprintf(buf, "%d-sss-cnv-pro-name", x->localzero);    x->s_cnv_pro_name = gensym(buf);
  sprintf(buf, "%d-sss-cnv-ins-name", x->localzero);    x->s_cnv_ins_name = gensym(buf);
  sprintf(buf, "%d-sss-sel-snap", x->localzero);        x->s_sel_snap = gensym(buf);
  sprintf(buf, "%d-sss-have-data", x->localzero);       x->s_have_data = gensym(buf);
  /* ins */
  for (int i=0; i<MAX_INS; i++)
    {
      x->ins[i].ex = E_NO;
      x->ins[i].name = s_empty;
      x->ins[i].localzero = 0;
      x->ins[i].globalzero = 0;
      x->ins[i].path_snap = s_empty;
      x->ins[i].sel_snap = 0;
      for (int j=0; j<MAX_SNAP; j++)
	x->ins[i].have_data[j] = 0;
      /* par */
      for (int j=0; j<MAX_PAR; j++)
	{
	  x->ins[i].par[j].ex = E_NO;
	  x->ins[i].par[j].type = s_empty;
	  x->ins[i].par[j].label = s_empty;
	  x->ins[i].par[j].min = 0.0;
	  x->ins[i].par[j].max = 0.0;
	  x->ins[i].par[j].step = 0.0;
	  x->ins[i].par[j].snd = s_empty;
	  x->ins[i].par[j].rcv = s_empty;
	  for (int k=0; k<MAX_SNAP; k++)
	    x->ins[i].par[j].data[k] = 0.0;
	}
      /* ar */
      for (int j=0; j<MAX_AR; j++)
	{
	  x->ins[i].ar[j].ex = E_NO;
	  x->ins[i].ar[j].name = s_empty;
	  for (int k=0; k<MAX_SNAP; k++)
	    {
	      if (x->ins[i].ar[j].data[k] != NULL)
		{
		  free(x->ins[i].ar[j].data[k]);
		  x->ins[i].ar[j].data[k] = NULL;
		}
	      x->ins[i].ar[j].len[k] = 0;
	    }
	}
    }
  /* buf */
  for (int j=0; j<MAX_PAR; j++)
    {
      x->buf_par[j] = 0.0;
    }
  for (int j=0; j<MAX_AR; j++)
    {
      if (x->buf_ar[j] != NULL)
	{
	  free(x->buf_ar[j]);
	  x->buf_ar[j] = NULL;
	}
      x->buf_ar_l[j] = 0;
    }
}

// abs_name (last .pd)
void sss_abs_name(t_sss *x, t_symbol *s)
{
  int i;
  char buf[MAX_ABS_NAME];
  int l = strlen(s->s_name);
  if (l < 4 || l >= MAX_ABS_NAME-1)
    {
      x->abs_name = s_empty;
      post("error: bad abs name: %s", s->s_name);
      return;
    }
  if (s->s_name[l-3] != '.'||
      s->s_name[l-2] != 'p'||
      s->s_name[l-1] != 'd')
    {
      x->abs_name = s_empty;
      post("error: bad abs name: %s", s->s_name);
      return;
    }
  for(i=0; i<l-3; i++)
    buf[i] = s->s_name[i];
  buf[i] = '\0';
  x->abs_name = gensym(buf);
}

// get env sss and make path
void sss_path(t_sss *x)
{
  char buf[MAX_STRING];
  // env
  char *var = getenv(ENV_PD_SSS);
  if (var != NULL)
    {
      x->path_sss = gensym(var);
    }
  else
    {
      x->path_sss = s_empty;
      post("error: env %s is not set", ENV_PD_SSS);
      return;
    }

  // ex or cr
  if (exorcr_dir(x->path_sss) != E_OK) { return; }

  sprintf(buf, "%s/pro", x->path_sss->s_name);
  x->path_allpro = gensym(buf);
  if (exorcr_dir(x->path_allpro) != E_OK) { return; }

  sprintf(buf, "%s/snap", x->path_sss->s_name);
  x->path_allsnap = gensym(buf);
  if (exorcr_dir(x->path_allsnap)!= E_OK) { return; }

  sprintf(buf, "%s/pro/%s", x->path_sss->s_name, x->abs_name->s_name);
  x->path_pro = gensym(buf);
  if (exorcr_dir(x->path_pro) != E_OK) { return; }

  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  sprintf(buf, "%s/snap/%s", x->path_sss->s_name, x->ins[i].name->s_name);
	  x->ins[i].path_snap = gensym(buf);
	  if (exorcr_dir(x->ins[i].path_snap) != E_OK) { return; }
	}
    }
}

void sss_get_info_par_return(t_sss *x, t_symbol *s, int ac, t_atom *av)
{
  char buf[MAX_STRING];

  t_symbol *name  = atom_getsymbolarg(0, ac, av);
  int localzero   = atom_getfloatarg(1, ac, av);
  int globalzero  = atom_getfloatarg(2, ac, av);
  int num         = atom_getfloatarg(3, ac, av);
  int par_num     = atom_getfloatarg(4, ac, av);
  t_symbol *type  = atom_getsymbolarg(5, ac, av);
  t_symbol *label = atom_getsymbolarg(6, ac, av);
  t_float min     = atom_getfloatarg(7, ac, av);
  t_float max     = atom_getfloatarg(8, ac, av);
  t_float step    = atom_getfloatarg(9, ac, av);

  // clip
  if (num < 0 || num >= MAX_INS)
    {
      post("error: bad ins num: %d", num);
      return;
    }
  if (par_num < 0 || par_num >= MAX_PAR)
    {
      post("error: bad par num: %d", par_num);
      return;
    }

  // check localzero
  if ((x->ins[num].localzero != 0) && (x->ins[num].localzero != localzero))
    {
      post("error: not unique num: %d", num);
      return;
    }

  // fill data
  x->ins[num].ex                   = E_YES;
  x->ins[num].name                 = name;
  x->ins[num].localzero            = localzero;
  x->ins[num].globalzero           = globalzero;
  x->ins[num].par[par_num].ex      = E_YES;
  x->ins[num].par[par_num].type    = type;
  x->ins[num].par[par_num].label   = label;
  x->ins[num].par[par_num].min     = min;
  x->ins[num].par[par_num].max     = max;
  x->ins[num].par[par_num].step    = step;
  sprintf(buf, "%d-sss-s-%d", localzero, par_num);
  x->ins[num].par[par_num].snd = gensym(buf);
  sprintf(buf, "%d-sss-r-%d", localzero, par_num);
  x->ins[num].par[par_num].rcv = gensym(buf);
  
  NOUSE(s);
}

void sss_get_info_ar_return(t_sss *x, t_symbol *s, int ac, t_atom *av)
{
  t_symbol *name  = atom_getsymbolarg(0, ac, av);
  int localzero   = atom_getfloatarg(1, ac, av);
  int globalzero  = atom_getfloatarg(2, ac, av);
  int num         = atom_getfloatarg(3, ac, av);
  int ar_num      = atom_getfloatarg(4, ac, av);
  t_symbol *aname = atom_getsymbolarg(5, ac, av);

  // clip
  if (num < 0 || num >= MAX_INS)
    {
      post("error: bad ins num: %d", num);
      return;
    }
  if (ar_num < 0 || ar_num >= MAX_AR)
    {
      post("error: bad ar num: %d", ar_num);
      return;
    }

  // check localzero
  if ((x->ins[num].localzero != 0) && (x->ins[num].localzero != localzero))
    {
      post("error: not unique num: %d", num);
      return;
    }

  // fill data
  x->ins[num].ex                 = E_YES;
  x->ins[num].name               = name;
  x->ins[num].localzero          = localzero;
  x->ins[num].globalzero         = globalzero;
  x->ins[num].ar[ar_num].ex      = E_YES;
  x->ins[num].ar[ar_num].name    = aname;
  
  NOUSE(s);
}

void sss_info(t_sss *x)
{
  post("localzero: %d", x->localzero);
  post("globalzero: %d", x->globalzero);
  post("abs name: %s", x->abs_name->s_name);
  post("pro name: %s", x->pro_name->s_name);
  post("path sss: %s", x->path_sss->s_name);
  post("path all pro: %s", x->path_allpro->s_name);
  post("path all snap: %s", x->path_allsnap->s_name);
  post("path pro: %s", x->path_pro->s_name);
  post("focus: %d", x->focus);
  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  post("ins num: %d", i);
	  post("ins name: %s", x->ins[i].name->s_name);
	  post("ins localzero: %d", x->ins[i].localzero);
	  post("ins globalzero: %d", x->ins[i].globalzero);
	  post("ins path snap: %s", x->ins[i].path_snap->s_name);
	  post("ins sel snap: %d", x->ins[i].sel_snap);
	  for (int j=0; j<MAX_PAR; j++)
	    {
	      if (x->ins[i].par[j].ex == E_YES)
		{
		  post("par: %d | %s %s | %g %g %g | %s %s", 
		       j,
		       x->ins[i].par[j].type->s_name,
		       x->ins[i].par[j].label->s_name,
		       x->ins[i].par[j].min,
		       x->ins[i].par[j].max,
		       x->ins[i].par[j].step,
		       x->ins[i].par[j].snd->s_name,
		       x->ins[i].par[j].rcv->s_name);
		}
	    }
	  for (int j=0; j<MAX_AR; j++)
	    {
	      if (x->ins[i].ar[j].ex == E_YES)
		{
		  post("ar: %d | %s", 
		       j,
		       x->ins[i].ar[j].name->s_name);
		}
	    }
	}
    }
}

void sss_set_abs_name(t_sss *x)
{
  t_atom a[1];
  SETSYMBOL(a, x->abs_name);
  if (x->s_cnv_abs_name->s_thing)
    typedmess(x->s_cnv_abs_name->s_thing, s_label, 1, a);
}

void sss_set_pro_name(t_sss *x)
{
  t_atom a[1];
  SETSYMBOL(a, x->pro_name);
  if (x->s_cnv_pro_name->s_thing)
    typedmess(x->s_cnv_pro_name->s_thing, s_label, 1, a);
}

void sss_set_ins_name(t_sss *x)
{
  char buf[MAX_STRING];
  sprintf(buf, "(%d)%s", x->focus, x->ins[x->focus].name->s_name);
  t_atom a[1];
  SETSYMBOL(a, gensym(buf));
  if (x->s_cnv_ins_name->s_thing)
    typedmess(x->s_cnv_ins_name->s_thing, s_label, 1, a);
}

void sss_set_pro_path(t_sss *x)
{
  if (x->s_path_pro->s_thing)
    pd_symbol(x->s_path_pro->s_thing, x->path_pro);
}

void sss_set_snap_path(t_sss *x)
{
  if (x->s_path_snap->s_thing)
    pd_symbol(x->s_path_snap->s_thing, x->ins[x->focus].path_snap);
}

void sss_set_sel_snap(t_sss *x)
{
  if (x->s_sel_snap->s_thing)
    pd_float(x->s_sel_snap->s_thing, (t_float)x->ins[x->focus].sel_snap);
}

void sss_set_have_data(t_sss *x)
{
  if (x->s_have_data->s_thing)
    {
      t_atom a[MAX_SNAP];
      for(int i=0; i<MAX_SNAP; i++)
	SETFLOAT(a+i, (t_float)x->ins[x->focus].have_data[i]);
      pd_list(x->s_have_data->s_thing, &s_list, MAX_SNAP, a);
    }
}

void sss_calc_focus(t_sss *x)
{
  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  x->focus = i;
	  if (x->s_focus->s_thing)
	    pd_float(x->s_focus->s_thing, (t_float)x->focus);
	  break;
	}
    }
}

void sss_focus(t_sss *x, t_floatarg f)
{
  x->focus = (f<0)?0:(f>MAX_INS-1)?MAX_INS-1:f;
}

void sss_sel_snap(t_sss *x, t_floatarg f)
{
  x->ins[x->focus].sel_snap = (f<0)?0:(f>MAX_SNAP-1)?MAX_SNAP-1:f;
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  set_par(x->ins[x->focus].par[j].rcv, 
		  x->ins[x->focus].par[j].data[x->ins[x->focus].sel_snap]);
	}
    }
}

void sss_snap_copy(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  x->buf_par[j] = get_par(x->ins[x->focus].par[j].snd);
	}
    }
}

void sss_snap_paste(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  set_par(x->ins[x->focus].par[j].rcv, x->buf_par[j]);
	}
    }
}

void sss_snap_save(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  x->ins[x->focus].par[j].data[x->ins[x->focus].sel_snap] =
	    get_par(x->ins[x->focus].par[j].snd);
	  /* post("save: ins=%d snap=%d n=%d v=%g",x->focus, x->ins[x->focus].sel_snap, j, get_par(x->ins[x->focus].par[j].snd)); */
	}
    }
  x->ins[x->focus].have_data[x->ins[x->focus].sel_snap] = 1;
}

void sss_snap_erase(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      x->ins[x->focus].par[j].data[x->ins[x->focus].sel_snap] = 0.0;
      set_par(x->ins[x->focus].par[j].rcv, 0.0);
    }
  x->ins[x->focus].have_data[x->ins[x->focus].sel_snap] = 0;
}

void sss_snap_save_as(t_sss *x, t_symbol *s)
{
  save_snap_to_file(&x->ins[x->focus], x->ins[x->focus].sel_snap, s->s_name);
}

void sss_snap_open(t_sss *x, t_symbol *s)
{
  open_file_to_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap, s->s_name);
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  set_par(x->ins[x->focus].par[j].rcv,
		  x->ins[x->focus].par[j].data[x->ins[x->focus].sel_snap]);
	}
    }
  x->ins[x->focus].have_data[x->ins[x->focus].sel_snap] = 1;
}

void sss_snap_load(t_sss *x, t_floatarg ni, t_floatarg ns)
{
  int ins  = (ni<0)?0:(ni>MAX_INS-1)?MAX_INS-1:ni;
  int snap = (ns<0)?0:(ns>MAX_SNAP-1)?MAX_SNAP-1:ns;
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[ins].par[j].ex == E_YES)
	{
	  set_par(x->ins[ins].par[j].rcv, x->ins[ins].par[j].data[snap]);
	}
    }
}

////////////////////////////////////////////////////////////////////////////////
// setup
void *sss_new(t_symbol *s, int ac, t_atom *av)
{
  t_sss *x = (t_sss *)pd_new(sss_class);
  outlet_new(&x->x_obj, 0);
  x->localzero = atom_getfloatarg(0, ac, av);
  x->globalzero = atom_getfloatarg(1, ac, av);
  return (void *)x;
  NOUSE(s);
}

void sss_setup(void)
{
  sss_class = class_new(gensym("sss"),
			(t_newmethod)sss_new,
			0,
			sizeof(t_sss),
			0, A_GIMME, 0);
  class_addmethod(sss_class,(t_method)sss_init,gensym("init"),0);
  class_addmethod(sss_class,(t_method)sss_abs_name,gensym("abs_name"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_path,gensym("path"),0);
  class_addmethod(sss_class,(t_method)sss_get_info_par_return,
		  gensym("get_info_par_return"), A_GIMME, 0);
  class_addmethod(sss_class,(t_method)sss_get_info_ar_return,
		  gensym("get_info_ar_return"), A_GIMME, 0);
  class_addmethod(sss_class,(t_method)sss_info,gensym("info"),0);
  class_addmethod(sss_class,(t_method)sss_set_abs_name,gensym("set_abs_name"),0);
  class_addmethod(sss_class,(t_method)sss_set_pro_name,gensym("set_pro_name"),0);
  class_addmethod(sss_class,(t_method)sss_set_ins_name,gensym("set_ins_name"),0);
  class_addmethod(sss_class,(t_method)sss_set_pro_path,gensym("set_pro_path"),0);
  class_addmethod(sss_class,(t_method)sss_set_snap_path,gensym("set_snap_path"),0);
  class_addmethod(sss_class,(t_method)sss_set_sel_snap,gensym("set_sel_snap"),0);
  class_addmethod(sss_class,(t_method)sss_set_have_data,gensym("set_have_data"),0);
  class_addmethod(sss_class,(t_method)sss_calc_focus,gensym("calc_focus"),0);
  class_addmethod(sss_class,(t_method)sss_focus,gensym("focus"),A_FLOAT,0);
  class_addmethod(sss_class,(t_method)sss_sel_snap,gensym("sel_snap"),A_FLOAT,0);
  class_addmethod(sss_class,(t_method)sss_snap_copy,gensym("snap_copy"),0);
  class_addmethod(sss_class,(t_method)sss_snap_paste,gensym("snap_paste"),0);
  class_addmethod(sss_class,(t_method)sss_snap_save,gensym("snap_save"),0);
  class_addmethod(sss_class,(t_method)sss_snap_erase,gensym("snap_erase"),0);
  class_addmethod(sss_class,(t_method)sss_snap_save_as,gensym("snap_save_as"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_snap_open,gensym("snap_open"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_snap_load,gensym("snap_load"),
		  A_FLOAT, A_FLOAT,0);
  s_empty = gensym("");
  s_label = gensym("label");
}
