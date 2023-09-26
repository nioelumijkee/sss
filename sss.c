#include "m_pd.h"
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h> // stat
#include <dirent.h>   // DIR opendir
#include <unistd.h> // access

////////////////////////////////////////////////////////////////////////////////
#define MAX_STRING 512
#define SIZE_PRO 8192 // (MAX_INS * MAX_SNAP) + (MAX_INS * MAX_AR)
#define MAX_INS 128
#define MAX_PAR 256
#define MAX_AR 32
#define MAX_SNAP 32
#define MAX_ABS_NAME 128
#define ENV_PD_SSS "PD_SSS"
#define E_NO 0
#define E_YES 1
#define E_OK 0
#define E_ERR 1
#define NOUSE(X) if(X){};
#define DEFAULT_PRO_NAME "default"
#define STR_SPLIT "========================================"
/* #define DEBUG(x) x */
#define DEBUG(x)

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
  int       size;
  t_float   *data;
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
  t_symbol *path_allar;
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
  /* randomize */
  unsigned int seed;
  t_float  rnd_amt;
} t_sss;

////////////////////////////////////////////////////////////////////////////////
static t_class *sss_class;
t_symbol *s_empty;
t_symbol *s_label;

////////////////////////////////////////////////////////////////////////////////
int sss_pd_open_array(t_symbol *s_arr,  // name
                  t_word **w_arr,   // word
                  t_garray **g_arr) // garray
{
  DEBUG(post("sss: debug: sss_pd_open_array: %s", s_arr->s_name));
  int len;
  t_word *i_w_arr;
  t_garray *i_g_arr;
  if (!(i_g_arr = (t_garray *)pd_findbyclass(s_arr, garray_class)))
    {
      post("sss: no such array: %s", s_arr->s_name);
      len = -1;
    }
  else if (!garray_getfloatwords(i_g_arr, &len, &i_w_arr))
    {
      post("sss: bad template: %s", s_arr->s_name);
      len = -1;
    }
  else
    {
      *w_arr = i_w_arr;
      *g_arr = i_g_arr;
    }
  return (len);
}

t_float sss_rndf(unsigned int *seed)
{
  *seed = *seed * 1103515245;
  *seed += 12345;
  t_float f = *seed * 0.000000000466;
  if (f>1)
    {
      int i = f;
      f = f -i;
    }
  return (f);
} 

int sss_exorcr_dir(t_symbol *p)
{
  DEBUG(post("sss: debug: sss_exorcr_dir: %s", p->s_name));
  int err;
  struct stat st;
  err = stat(p->s_name, &st);
  if (err != 0)
    {
      // create
      err = mkdir(p->s_name, S_IRWXU);
      if (err != 0)
	{
	  post("sss: error: mkdir or stat: %s", p->s_name);
	  return (E_ERR);
	}
      else
	{
	  post("sss: mkdir: %s", p->s_name);
	  err = stat(p->s_name, &st);
	}
    }
  if (!S_ISDIR(st.st_mode)) 
    {
      post("sss: error: not dir: %s", p->s_name);
      return (E_ERR);
    }
  // access
  if (access(p->s_name, R_OK|W_OK|X_OK) < 0) 
    {
      post("sss: error: access to: %s", p->s_name);
      return (E_ERR);
    }
  return (E_OK);
}

t_float sss_get_par(t_symbol *n)
{
  t_float *x_floatstar;
  x_floatstar = value_get(n);
  return(*x_floatstar);
}

void sss_set_par(t_symbol *n, t_float f)
{
  if (n->s_thing) { pd_float(n->s_thing, f); }
}

void save_snap_to_file(t_ins *ins, int snap, const char *filename)
{
  DEBUG(post("sss: debug: save_snap_to_file: ins: %s snap: %d file: %s",
	     ins->name->s_name, snap, filename));
  int size=0;
  float buf[MAX_PAR];
  FILE *fd;
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  buf[size] = ins->par[j].data[snap];
	  size++;
	}
    }
  fd = fopen(filename, "wb");
  if (fd == NULL)
    {
      post("sss: error: open file: %s", filename);
      return;
    }
  fwrite(buf, sizeof(float), size, fd);
  fclose(fd);
}

void sss_save_ar_to_file(t_ins *ins, int n, const char *filename)
{
  DEBUG(post("sss: debug: sss_save_ar_to_file: ins: %s n: %d file: %s",
	     ins->name->s_name, n, filename));
  float *buf = NULL;
  FILE *fd;
  t_word *w;
  t_garray *g;
  int size;
  /* copy to buf */
  size = sss_pd_open_array(ins->ar[n].name, &w ,&g);
  if (size <= 0)
    {
      post("sss: error: open array: %s", ins->ar[n].name->s_name);
      return;
    }
  buf = malloc(size * sizeof(float));
  if (buf == NULL)
    {
      post("sss: error: malloc: %s", ins->ar[n].name->s_name);
      return;
    }
  for (int i=0; i<size; i++)
    buf[i] = w[i].w_float;
  /* file */
  fd = fopen(filename, "wb");
  if (fd == NULL)
    {
      post("sss: error: open file: %s", filename);
      return;
    }
  fwrite(buf, sizeof(float), size, fd);
  fclose(fd);
  free(buf);
}

void sss_open_file_to_snap(t_ins *ins, int snap, const char *filename)
{
  DEBUG(post("sss: debug: sss_open_file_to_snap: ins: %s snap: %d file: %s",
	     ins->name->s_name, snap, filename));
  int size=0;
  float buf;
  FILE *fd;
  fd = fopen(filename, "rb");
  if (fd == NULL)
    {
      post("sss: error: open file: %s", filename);
      return;
    }
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  fread(&buf, sizeof(float), 1, fd);
	  ins->par[j].data[snap] = (t_float)buf;
	  size++;
	}
    }
  fclose(fd);
  ins->have_data[snap] = 1;
}

void sss_open_file_to_ar(t_ins *ins, int n, const char *filename)
{
  DEBUG(post("sss: debug: sss_open_file_to_ar: ins: %s n: %d file: %s",
	     ins->name->s_name, n, filename));
  int file_size;
  int size=0;
  float buf;
  FILE *fd;
  t_word *w;
  t_garray *g;
  /* open file */
  fd = fopen(filename, "rb");
  if (fd == NULL)
    {
      post("sss: error: open file: %s", filename);
      return;
    }
  /* file size */
  fseek(fd, 0, SEEK_END);
  file_size = (int)ftell(fd) / sizeof(float);
  fseek(fd, 0, SEEK_SET);
  /* size ar */
  size = sss_pd_open_array(ins->ar[n].name, &w ,&g);
  if (size <= 0)
    {
      post("sss: error: open array: %s", ins->ar[n].name->s_name);
      return;
    }
  garray_resize(g, file_size);
  size = sss_pd_open_array(ins->ar[n].name, &w ,&g);
  if (size != file_size)
    {
      post("sss: error: resize array: %s", ins->ar[n].name->s_name);
      return;
    }
  // copy
  for(int j=0; j<file_size; j++)
    {
      fread(&buf, sizeof(float), 1, fd);
      w[j].w_float = (t_float)buf;
    }
  garray_redraw(g);
  fclose(fd);
}

void sss_get_snap(t_ins *ins, int snap)
{
  DEBUG(post("sss: debug: sss_get_snap"));
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  ins->par[j].data[snap] = sss_get_par(ins->par[j].snd);
	}
    }
  ins->have_data[snap] = 1;
}

void sss_erase_snap(t_ins *ins, int snap)
{
  DEBUG(post("sss: debug: sss_erase_snap"));
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  ins->par[j].data[snap] = 0.0;
	}
    }
  ins->have_data[snap] = 0;
}

void sss_set_snap(t_ins *ins, int snap)
{
  DEBUG(post("sss: debug: sss_set_snap"));
  for(int j=0; j<MAX_PAR; j++)
    {
      if (ins->par[j].ex == E_YES)
	{
	  sss_set_par(ins->par[j].rcv, ins->par[j].data[snap]);
	}
    }
}

////////////////////////////////////////////////////////////////////////////////
// save / open pro
void save_pro_to_file(t_sss *x)
{
  DEBUG(post("sss: debug: save_pro_to_file"));
  char buf[SIZE_PRO];
  char bufs[MAX_STRING];
  FILE *fd;
  /* save pro */
  int pos = 0;
  int k;
  /* snap */
  for(int i=0; i<MAX_INS; i++)
    {
      for(int j=0; j<MAX_SNAP; j++)
	{
	  if (x->ins[i].ex == E_YES)
	    {
	      k = x->ins[i].have_data[j];
	      if (j == x->ins[i].sel_snap)
		k = 2;
	    }
	  else
	    k = 0;
	  buf[pos] = k;
	  pos++;
	}
    }
  /* ar */
  for(int i=0; i<MAX_INS; i++)
    {
      for(int j=0; j<MAX_AR; j++)
	{
	  if (x->ins[i].ex == E_YES)
	    {
	      if (x->ins[i].ar[j].ex == E_YES)
		k = 1;
	      else
		k = 0;
	    }
	  else
	    k = 0;
	  buf[pos] = k;
	  pos++;
	}
    }
  /* save file */
  sprintf(bufs, "%s/%s/%s", 
	  x->path_allpro->s_name,
	  x->abs_name->s_name,
	  x->pro_name->s_name);
  fd = fopen(bufs, "wb");
  if (fd == NULL)
    {
      post("sss: error: open file: %s", bufs);
      return;
    }
  fwrite(buf, sizeof(char), SIZE_PRO, fd);
  fclose(fd);
  /* save snap */
  for(int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  for(int j=0; j<MAX_SNAP; j++)
	    {
	      if (x->ins[i].have_data[j] == 1)
		{
		  sprintf(bufs, "%s/%s/.%s.%s.%d.%d", 
			  x->path_allsnap->s_name,
			  x->ins[i].name->s_name,
			  x->abs_name->s_name,
			  x->pro_name->s_name,
			  i, // ins num
			  j); // snap num
		  save_snap_to_file(&x->ins[i], j, (const char *)bufs);
		}
	    }
	}
    }
  /* save ar */
  for(int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  for(int j=0; j<MAX_AR; j++)
	    {
	      if (x->ins[i].ar[j].ex == E_YES)
		{
		  sprintf(bufs, "%s/%s/.%s.%s.%d.%d", 
			  x->path_allar->s_name,
			  x->ins[i].name->s_name,
			  x->abs_name->s_name,
			  x->pro_name->s_name,
			  i, // ins num
			  j); // ar num
		  sss_save_ar_to_file(&x->ins[i], j, (const char *)bufs);
		}
	    }
	}
    }
}

void open_file_pro(t_sss *x)
{
  DEBUG(post("sss: debug: open_file_pro"));
  char buf;
  char bufs[MAX_STRING];
  FILE *fd;
  sprintf(bufs, "%s/%s/%s", 
	  x->path_allpro->s_name,
	  x->abs_name->s_name,
	  x->pro_name->s_name);
  fd = fopen(bufs, "rb");
  if (fd == NULL)
    {
      post("sss: error: open file: %s", bufs);
      return;
    }
  // load snap
  for(int i=0; i<MAX_INS; i++)
    {
      for(int j=0; j<MAX_SNAP; j++)
	{
	  fread(&buf, sizeof(char), 1, fd);
	  if (buf >= 1)
	    {
	      sprintf(bufs, "%s/%s/.%s.%s.%d.%d", 
		      x->path_allsnap->s_name,
		      x->ins[i].name->s_name,
		      x->abs_name->s_name,
		      x->pro_name->s_name,
		      i, // ins num
		      j); // snap num
	      sss_open_file_to_snap(&x->ins[i], j, (const char *)bufs);
	      if (buf == 2)
		x->ins[i].sel_snap = j;
	    }
	}
    }
  // load ar
  for(int i=0; i<MAX_INS; i++)
    {
      for(int j=0; j<MAX_AR; j++)
	{
	  fread(&buf, sizeof(char), 1, fd);
	  if (buf >= 1)
	    {
	      sprintf(bufs, "%s/%s/.%s.%s.%d.%d", 
		      x->path_allar->s_name,
		      x->ins[i].name->s_name,
		      x->abs_name->s_name,
		      x->pro_name->s_name,
		      i, // ins num
		      j); // ar num
	      sss_open_file_to_ar(&x->ins[i], j, (const char *)bufs);
	    }
	}
    }
  fclose(fd);
}

////////////////////////////////////////////////////////////////////////////////
void sss_init(t_sss *x)
{
  DEBUG(post("sss: debug: sss_init"));
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
	  x->ins[i].par[j].type = s_empty;
	  x->ins[i].ar[j].name = s_empty;
	  x->ins[i].ar[j].size = 0;
	  x->ins[i].ar[j].data = NULL;
	}
    }
  /* buf */
  for (int j=0; j<MAX_PAR; j++)
    {
      x->buf_par[j] = 0.0;
    }
}

// clear data. free data for arrays
void sss_init_mem(t_sss *x)
{
  DEBUG(post("sss: debug: sss_init_mem"));
  /* ins */
  for (int i=0; i<MAX_INS; i++)
    {
      x->ins[i].sel_snap = 0;
      for (int j=0; j<MAX_SNAP; j++)
	x->ins[i].have_data[j] = 0;
      /* par */
      for (int j=0; j<MAX_PAR; j++)
	{
	  for (int k=0; k<MAX_SNAP; k++)
	    x->ins[i].par[j].data[k] = 0.0;
	}
    }
}

// abs_name
void sss_abs_name(t_sss *x, t_symbol *s)
{
  DEBUG(post("sss: debug: sss_abs_name"));
  x->abs_name = s;
}

// get env sss and make path
void sss_path(t_sss *x)
{
  DEBUG(post("sss: debug: sss_path"));
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
      post("sss: error: env %s is not set", ENV_PD_SSS);
      return;
    }

  // ex or cr
  if (sss_exorcr_dir(x->path_sss) != E_OK) { return; }

  sprintf(buf, "%s/pro", x->path_sss->s_name);
  x->path_allpro = gensym(buf);
  if (sss_exorcr_dir(x->path_allpro) != E_OK) { return; }

  sprintf(buf, "%s/snap", x->path_sss->s_name);
  x->path_allsnap = gensym(buf);
  if (sss_exorcr_dir(x->path_allsnap)!= E_OK) { return; }

  sprintf(buf, "%s/ar", x->path_sss->s_name);
  x->path_allar = gensym(buf);
  if (sss_exorcr_dir(x->path_allar)!= E_OK) { return; }

  sprintf(buf, "%s/pro/%s", x->path_sss->s_name, x->abs_name->s_name);
  x->path_pro = gensym(buf);
  if (sss_exorcr_dir(x->path_pro) != E_OK) { return; }

  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  sprintf(buf, "%s/snap/%s", x->path_sss->s_name, x->ins[i].name->s_name);
	  x->ins[i].path_snap = gensym(buf);
	  if (sss_exorcr_dir(x->ins[i].path_snap) != E_OK) { return; }
	}
    }

  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  int ex = 0;
	  for (int j=0; j<MAX_AR; j++)
	    {
	      if (x->ins[i].ar[j].ex == E_YES)
		{
		  ex = 1;
		  break;
		}
	    }
	  if (ex)
	    {
	      sprintf(buf, "%s/ar/%s", x->path_sss->s_name, x->ins[i].name->s_name);
	      x->ins[i].path_snap = gensym(buf);
	      if (sss_exorcr_dir(x->ins[i].path_snap) != E_OK) { return; }
	    }
	}
    }
}

void sss_get_info_par_return(t_sss *x, t_symbol *s, int ac, t_atom *av)
{
  DEBUG(post("sss: debug: sss_get_info_par_return"));
  char buf[MAX_STRING];

  t_symbol *ins_name = atom_getsymbolarg(0, ac, av);
  int localzero      = atom_getfloatarg(1, ac, av);
  int globalzero     = atom_getfloatarg(2, ac, av);
  int ins_num        = atom_getfloatarg(3, ac, av);
  int par_num        = atom_getfloatarg(4, ac, av);
  t_symbol *type     = atom_getsymbolarg(5, ac, av);
  t_symbol *label    = atom_getsymbolarg(6, ac, av);
  t_float min        = atom_getfloatarg(7, ac, av);
  t_float max        = atom_getfloatarg(8, ac, av);
  t_float step       = atom_getfloatarg(9, ac, av);

  // clip
  if (ins_num < 0 || ins_num >= MAX_INS)
    {
      post("sss: error: bad ins num: %d", ins_num);
      return;
    }
  if (par_num < 0 || par_num >= MAX_PAR)
    {
      post("sss: error: bad par num: %d", par_num);
      return;
    }

  // check localzero
  if ((x->ins[ins_num].localzero != 0) && (x->ins[ins_num].localzero != localzero))
    {
      post("sss: error: not unique num: %d", ins_num);
      return;
    }

  // fill data
  x->ins[ins_num].ex                   = E_YES;
  x->ins[ins_num].name                 = ins_name;
  x->ins[ins_num].localzero            = localzero;
  x->ins[ins_num].globalzero           = globalzero;
  x->ins[ins_num].par[par_num].ex      = E_YES;
  x->ins[ins_num].par[par_num].type    = type;
  x->ins[ins_num].par[par_num].label   = label;
  x->ins[ins_num].par[par_num].min     = min;
  x->ins[ins_num].par[par_num].max     = max;
  x->ins[ins_num].par[par_num].step    = step;
  sprintf(buf, "%d-sss-s-%d", localzero, par_num);
  x->ins[ins_num].par[par_num].snd = gensym(buf);
  sprintf(buf, "%d-sss-r-%d", localzero, par_num);
  x->ins[ins_num].par[par_num].rcv = gensym(buf);
  
  NOUSE(s);
}

void sss_get_info_ar_return(t_sss *x, t_symbol *s, int ac, t_atom *av)
{
  DEBUG(post("sss: debug: sss_get_info_ar_return"));
  t_symbol *ins_name = atom_getsymbolarg(0, ac, av);
  int localzero      = atom_getfloatarg(1, ac, av);
  int globalzero     = atom_getfloatarg(2, ac, av);
  int ins_num        = atom_getfloatarg(3, ac, av);
  int ar_num         = atom_getfloatarg(4, ac, av);
  t_symbol *ar_name  = atom_getsymbolarg(5, ac, av);

  // clip
  if (ins_num < 0 || ins_num >= MAX_INS)
    {
      post("sss: error: bad ins num: %d", ins_num);
      return;
    }
  if (ar_num < 0 || ar_num >= MAX_AR)
    {
      post("sss: error: bad ar num: %d", ar_num);
      return;
    }

  // check localzero
  if ((x->ins[ins_num].localzero != 0) && (x->ins[ins_num].localzero != localzero))
    {
      post("sss: error: not unique num: %d", ins_num);
      return;
    }

  // fill data
  x->ins[ins_num].ex                 = E_YES;
  x->ins[ins_num].name               = ins_name;
  x->ins[ins_num].localzero          = localzero;
  x->ins[ins_num].globalzero         = globalzero;
  x->ins[ins_num].ar[ar_num].ex      = E_YES;
  x->ins[ins_num].ar[ar_num].name    = ar_name;
  
  NOUSE(s);
}

void sss_test(t_sss *x)
{
  DEBUG(post("sss: debug: sss_test"));
  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  for (int j=0; j<MAX_PAR; j++)
	    {
	      if (x->ins[i].par[j].ex == E_YES)
		{
		  sss_get_par(x->ins[i].par[j].snd);
		}
	    }
	}
    }
}

void sss_info(t_sss *x)
{
  post(STR_SPLIT);
  post("sss: localzero: %d", x->localzero);
  post("sss: globalzero: %d", x->globalzero);
  post("sss: abs name: %s", x->abs_name->s_name);
  post("sss: pro name: %s", x->pro_name->s_name);
  post("sss: path sss: %s", x->path_sss->s_name);
  post("sss: path all pro: %s", x->path_allpro->s_name);
  post("sss: path all snap: %s", x->path_allsnap->s_name);
  post("sss: path all ar: %s", x->path_allar->s_name);
  post("sss: path pro: %s", x->path_pro->s_name);
  post("sss: focus: %d", x->focus);
  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  post(STR_SPLIT);
	  post("sss: ins num: %d", i);
	  post("sss: ins name: %s", x->ins[i].name->s_name);
	  post("sss: ins localzero: %d", x->ins[i].localzero);
	  post("sss: ins globalzero: %d", x->ins[i].globalzero);
	  post("sss: ins path snap: %s", x->ins[i].path_snap->s_name);
	  post("sss: ins sel snap: %d", x->ins[i].sel_snap);
	  for (int j=0; j<MAX_PAR; j++)
	    {
	      if (x->ins[i].par[j].ex == E_YES)
		{
		  post("sss: par: %d | %s %s | %g %g %g | %s %s", 
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
		  post("sss: ar: %d | %s | %d", 
		       j,
		       x->ins[i].ar[j].name->s_name,
		       x->ins[i].ar[j].size);
		}
	    }
	}
    }
}

void sss_set_abs_name(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_abs_name"));
  t_atom a[1];
  SETSYMBOL(a, x->abs_name);
  if (x->s_cnv_abs_name->s_thing)
    typedmess(x->s_cnv_abs_name->s_thing, s_label, 1, a);
}

void sss_set_pro_name(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_pro_name"));
  t_atom a[1];
  SETSYMBOL(a, x->pro_name);
  if (x->s_cnv_pro_name->s_thing)
    typedmess(x->s_cnv_pro_name->s_thing, s_label, 1, a);
}

void sss_set_ins_name(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_ins_name"));
  char buf[MAX_STRING];
  sprintf(buf, "(%d)%s", x->focus, x->ins[x->focus].name->s_name);
  t_atom a[1];
  SETSYMBOL(a, gensym(buf));
  if (x->s_cnv_ins_name->s_thing)
    typedmess(x->s_cnv_ins_name->s_thing, s_label, 1, a);
}

void sss_set_pro_path(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_pro_path"));
  if (x->s_path_pro->s_thing)
    pd_symbol(x->s_path_pro->s_thing, x->path_pro);
}

void sss_set_snap_path(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_snap_path"));
  if (x->s_path_snap->s_thing)
    pd_symbol(x->s_path_snap->s_thing, x->ins[x->focus].path_snap);
}

void sss_set_sel_snap(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_sel_snap"));
  if (x->s_sel_snap->s_thing)
    pd_float(x->s_sel_snap->s_thing, (t_float)x->ins[x->focus].sel_snap);
}

void sss_set_have_data(t_sss *x)
{
  DEBUG(post("sss: debug: sss_set_have_data"));
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
  DEBUG(post("sss: debug: sss_calc_focus"));
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
  DEBUG(post("sss: debug: sss_focus: %g", f));
  x->focus = (f<0)?0:(f>MAX_INS-1)?MAX_INS-1:f;
}

////////////////////////////////////////////////////////////////////////////////
// snap
void sss_snap(t_sss *x, t_floatarg f1, t_floatarg f2)
{
  DEBUG(post("sss: debug: sss_snap"));
  int ins  = (f1<0)?0:(f1>MAX_INS-1)?MAX_INS-1:f1;
  int snap = (f2<0)?0:(f2>MAX_SNAP-1)?MAX_SNAP-1:f2;
  x->ins[ins].sel_snap = snap;
  sss_set_snap(&x->ins[ins], snap);
}

void sss_sel_snap(t_sss *x, t_floatarg f)
{
  DEBUG(post("sss: debug: sss_sel_snap"));
  x->ins[x->focus].sel_snap = (f<0)?0:(f>MAX_SNAP-1)?MAX_SNAP-1:f;
  sss_set_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap);
}

void sss_snap_copy(t_sss *x)
{
  DEBUG(post("sss: debug: sss_snap_copy"));
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  x->buf_par[j] = sss_get_par(x->ins[x->focus].par[j].snd);
	}
    }
}

void sss_snap_paste(t_sss *x)
{
  DEBUG(post("sss: debug: sss_snap_paste"));
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  x->ins[x->focus].par[j].data[x->ins[x->focus].sel_snap] = x->buf_par[j];
	}
    }
  sss_set_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap);
}

void sss_snap_save(t_sss *x)
{
  DEBUG(post("sss: debug: sss_snap_save"));
  sss_get_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap);
}

void sss_snap_erase(t_sss *x)
{
  DEBUG(post("sss: debug: sss_snap_erase"));
  sss_erase_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap);
  sss_set_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap);
}

void sss_snap_save_as(t_sss *x, t_symbol *s)
{
  DEBUG(post("sss: debug: sss_snap_save_as: %s", s->s_name));
  save_snap_to_file(&x->ins[x->focus], x->ins[x->focus].sel_snap, s->s_name);
}

void sss_snap_open(t_sss *x, t_symbol *s)
{
  DEBUG(post("sss: debug: sss_snap_open: %s", s->s_name));
  sss_open_file_to_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap, s->s_name);
  sss_set_snap(&x->ins[x->focus], x->ins[x->focus].sel_snap);
}

void sss_snap_load(t_sss *x, t_floatarg ni, t_floatarg ns)
{
  DEBUG(post("sss: debug: sss_snap_load"));
  int ins  = (ni<0)?0:(ni>MAX_INS-1)?MAX_INS-1:ni;
  int snap = (ns<0)?0:(ns>MAX_SNAP-1)?MAX_SNAP-1:ns;
  sss_set_snap(&x->ins[ins], snap);
}

void sss_snap_load_all_sel(t_sss *x)
{
  DEBUG(post("sss: debug: sss_snap_load_all_sel"));
  for (int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  sss_set_snap(&x->ins[i], x->ins[i].sel_snap);
	}
    }
}

////////////////////////////////////////////////////////////////////////////////
// pro
void sss_pro_save(t_sss *x)
{
  DEBUG(post("sss: debug: sss_pro_save"));
  // save all have data
  for(int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  sss_get_snap(&x->ins[i], x->ins[i].sel_snap);
	}
    }
  save_pro_to_file(x);
}

void sss_pro_save_as(t_sss *x, t_symbol *s)
{
  DEBUG(post("sss: debug: sss_pro_save_as"));
  x->pro_name = s;
  // save all have data
  for(int i=0; i<MAX_INS; i++)
    {
      if (x->ins[i].ex == E_YES)
	{
	  sss_get_snap(&x->ins[i], x->ins[i].sel_snap);
	}
    }
  save_pro_to_file(x);
}

void sss_pro_open(t_sss *x, t_symbol *s)
{
  x->pro_name = s;
  open_file_pro(x);
}

////////////////////////////////////////////////////////////////////////////////
// randomize
void sss_rnd_amt(t_sss *x, t_floatarg f)
{
  x->rnd_amt = (f<0)?0:(f>1)?1:f;
}

void sss_rnd_nbx(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  if (!strcmp(x->ins[x->focus].par[j].type->s_name, "nbx"))
	    {
	      t_float f = sss_rndf(&x->seed);
	      f = (f-0.5) * x->rnd_amt;
	      t_float dif = x->ins[x->focus].par[j].max - x->ins[x->focus].par[j].min;
	      f = dif * f;
	      t_float cur = sss_get_par(x->ins[x->focus].par[j].snd);
	      cur = cur + f;
	      if (cur < x->ins[x->focus].par[j].min)
		cur = x->ins[x->focus].par[j].min;
	      if (cur > x->ins[x->focus].par[j].max)
		cur = x->ins[x->focus].par[j].max;
	      sss_set_par(x->ins[x->focus].par[j].rcv, cur);
	    }
	}
    }
}

void sss_rnd_slider(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  if ((!strcmp(x->ins[x->focus].par[j].type->s_name, "hsl")) ||
	      (!strcmp(x->ins[x->focus].par[j].type->s_name, "vsl")))
	    {
	      t_float f = sss_rndf(&x->seed);
	      f = (f-0.5) * x->rnd_amt;
	      t_float dif = x->ins[x->focus].par[j].max - x->ins[x->focus].par[j].min;
	      f = dif * f;
	      t_float cur = sss_get_par(x->ins[x->focus].par[j].snd);
	      cur = cur + f;
	      if (cur < x->ins[x->focus].par[j].min)
		cur = x->ins[x->focus].par[j].min;
	      if (cur > x->ins[x->focus].par[j].max)
		cur = x->ins[x->focus].par[j].max;
	      sss_set_par(x->ins[x->focus].par[j].rcv, cur);
	    }
	}
    }
}

void sss_rnd_tgl(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  if ((!strcmp(x->ins[x->focus].par[j].type->s_name, "tgl")))
	    {
	      t_float f = sss_rndf(&x->seed);
	      if (f>0.65)
		f = 1;
	      else
		f = 0;
	      sss_set_par(x->ins[x->focus].par[j].rcv, f);
	    }
	}
    }
}

void sss_rnd_radio(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  if ((!strcmp(x->ins[x->focus].par[j].type->s_name, "hrd")) ||
	      (!strcmp(x->ins[x->focus].par[j].type->s_name, "vrd")))
	    {
	      t_float f = sss_rndf(&x->seed);
	      f = (f-0.5) * x->rnd_amt;
	      t_float dif = x->ins[x->focus].par[j].max - x->ins[x->focus].par[j].min;
	      f = dif * f;
	      t_float cur = sss_get_par(x->ins[x->focus].par[j].snd);
	      cur = cur + f;
	      if (cur < x->ins[x->focus].par[j].min)
		cur = x->ins[x->focus].par[j].min;
	      if (cur > x->ins[x->focus].par[j].max)
		cur = x->ins[x->focus].par[j].max;
	      sss_set_par(x->ins[x->focus].par[j].rcv, (int)cur);
	    }
	}
    }
}

void sss_rnd_nknob(t_sss *x)
{
  for(int j=0; j<MAX_PAR; j++)
    {
      if (x->ins[x->focus].par[j].ex == E_YES)
	{
	  if (!strcmp(x->ins[x->focus].par[j].type->s_name, "n_knob"))
	    {
	      t_float f = sss_rndf(&x->seed);
	      f = (f-0.5) * x->rnd_amt;
	      t_float dif = x->ins[x->focus].par[j].max - x->ins[x->focus].par[j].min;
	      f = dif * f;
	      t_float cur = sss_get_par(x->ins[x->focus].par[j].snd);
	      cur = cur + f;
	      if (cur < x->ins[x->focus].par[j].min)
		cur = x->ins[x->focus].par[j].min;
	      if (cur > x->ins[x->focus].par[j].max)
		cur = x->ins[x->focus].par[j].max;
	      sss_set_par(x->ins[x->focus].par[j].rcv, cur);
	    }
	}
    }
}

////////////////////////////////////////////////////////////////////////////////
// setup
void *sss_new(t_symbol *s, int ac, t_atom *av)
{
  DEBUG(post("sss: debug: sss_new"));
  t_sss *x = (t_sss *)pd_new(sss_class);
  outlet_new(&x->x_obj, 0);
  x->localzero = atom_getfloatarg(0, ac, av);
  x->globalzero = atom_getfloatarg(1, ac, av);
  x->seed = (long)x;
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
  class_addmethod(sss_class,(t_method)sss_init_mem,gensym("init_mem"),0);
  class_addmethod(sss_class,(t_method)sss_abs_name,gensym("abs_name"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_path,gensym("path"),0);
  class_addmethod(sss_class,(t_method)sss_get_info_par_return,
		  gensym("get_info_par_return"),A_GIMME,0);
  class_addmethod(sss_class,(t_method)sss_get_info_ar_return,
		  gensym("get_info_ar_return"),A_GIMME,0);
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
  class_addmethod(sss_class,(t_method)sss_snap,gensym("snap"),A_FLOAT,A_FLOAT,0);
  class_addmethod(sss_class,(t_method)sss_sel_snap,gensym("sel_snap"),A_FLOAT,0);
  class_addmethod(sss_class,(t_method)sss_snap_copy,gensym("snap_copy"),0);
  class_addmethod(sss_class,(t_method)sss_snap_paste,gensym("snap_paste"),0);
  class_addmethod(sss_class,(t_method)sss_snap_save,gensym("snap_save"),0);
  class_addmethod(sss_class,(t_method)sss_snap_erase,gensym("snap_erase"),0);
  class_addmethod(sss_class,(t_method)sss_snap_save_as,gensym("snap_save_as"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_snap_open,gensym("snap_open"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_snap_load,
		  gensym("snap_load"),A_FLOAT,A_FLOAT,0);
  class_addmethod(sss_class,(t_method)sss_snap_load_all_sel,
		  gensym("snap_load_all_sel"),0);
  class_addmethod(sss_class,(t_method)sss_pro_save,gensym("pro_save"),0);
  class_addmethod(sss_class,(t_method)sss_pro_save_as,gensym("pro_save_as"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_pro_open,gensym("pro_open"),A_SYMBOL,0);
  class_addmethod(sss_class,(t_method)sss_test,gensym("test"),0);
  class_addmethod(sss_class,(t_method)sss_rnd_amt,gensym("rnd_amt"),A_FLOAT,0);
  class_addmethod(sss_class,(t_method)sss_rnd_nbx,gensym("rnd_nbx"),0);
  class_addmethod(sss_class,(t_method)sss_rnd_slider,gensym("rnd_slider"),0);
  class_addmethod(sss_class,(t_method)sss_rnd_radio,gensym("rnd_radio"),0);
  class_addmethod(sss_class,(t_method)sss_rnd_tgl,gensym("rnd_tgl"),0);
  class_addmethod(sss_class,(t_method)sss_rnd_nknob,gensym("rnd_nknob"),0);
  s_empty = gensym("");
  s_label = gensym("label");
}
