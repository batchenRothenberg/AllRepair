
/*  -*- Last-Edit:  Fri Jan 29 11:13:27 1993 by Tarak S. Goradia; -*- */
/* $Log: tcas.c,v $
 * Revision 1.2  1993/03/12  19:29:50  foster
 * Correct logic bug which didn't allow output of 2 - hf
 * */

#include <stdio.h>
#include <assert.h>

#define OLEV       600		/* in feets/minute */
#define MAXALTDIFF 600		/* max altitude difference in feet */
#define MINSEP     300          /* min separation in feet */
#define NOZCROSS   100		/* in feet */
#define OLEV_correct       600    /* in feets/minute */
#define MAXALTDIFF_correct 600    /* max altitude difference in feet */
#define MINSEP_correct     300          /* min separation in feet */
#define NOZCROSS_correct   100    /* in feet */
				/* variables */

typedef int bool;

int Cur_Vertical_Sep;
bool High_Confidence;
bool Two_of_Three_Reports_Valid;

int Own_Tracked_Alt;
int Own_Tracked_Alt_Rate;
int Other_Tracked_Alt;

int Alt_Layer_Value;		/* 0, 1, 2, 3 */
int Positive_RA_Alt_Thresh[4];

int Up_Separation;
int Down_Separation;

				/* state variables */
int Other_RAC;			/* NO_INTENT, DO_NOT_CLIMB, DO_NOT_DESCEND */
#define NO_INTENT 0
#define DO_NOT_CLIMB 1
#define DO_NOT_DESCEND 2
#define NO_INTENT_correct 0
#define DO_NOT_CLIMB_correct 1
#define DO_NOT_DESCEND_correct 2

int Other_Capability;		/* TCAS_TA, OTHER */
#define TCAS_TA 1
#define OTHER 2
#define TCAS_TA_correct 1
#define OTHER_correct 2

int Climb_Inhibit;		/* true/false */

#define UNRESOLVED 0
#define UPWARD_RA 1
#define DOWNWARD_RA 2
#define UNRESOLVED_correct 0
#define UPWARD_RA_correct 1
#define DOWNWARD_RA_correct 2

//bat
int  ALIM();
int  Inhibit_Biased_Climb();
bool   Non_Crossing_Biased_Climb();
bool   Non_Crossing_Biased_Descend();
bool   Own_Below_Threat();
bool   Own_Above_Threat();
int  alt_sep_test();
int  ALIM_correct();
int  Inhibit_Biased_Climb_correct();
bool   Non_Crossing_Biased_Climb_correct();
bool   Non_Crossing_Biased_Descend_correct();
bool   Own_Below_Threat_correct();
bool   Own_Above_Threat_correct();
int  alt_sep_test_correct();

void initialize()
{
    Positive_RA_Alt_Thresh[0] = 400;
    Positive_RA_Alt_Thresh[1] = 500;
    Positive_RA_Alt_Thresh[2] = 640;
    Positive_RA_Alt_Thresh[3] = 740;
}

int ALIM ()
{
 return Positive_RA_Alt_Thresh[Alt_Layer_Value];
}

int Inhibit_Biased_Climb ()
{
    return (Climb_Inhibit ? Up_Separation + NOZCROSS : Up_Separation);
}

bool Non_Crossing_Biased_Climb()
{
    int upward_preferred;
    int upward_crossing_situation;
    bool result;

    //upward_preferred = Inhibit_Biased_Climb() > Down_Separation;
    if (Inhibit_Biased_Climb() > Down_Separation)
    {
	result = !(Own_Below_Threat()) || ((Own_Below_Threat()) && (!(Down_Separation >= ALIM())));
    }
    else
    {	
	result = Own_Above_Threat() && (Cur_Vertical_Sep >= MINSEP) && (Up_Separation >= ALIM());
    }
    return result;
}

bool Non_Crossing_Biased_Descend()
{
    int upward_preferred;
    int upward_crossing_situation;
    bool result;

    //upward_preferred = Inhibit_Biased_Climb() > Down_Separation;
    if (Inhibit_Biased_Climb() > Down_Separation)
    {
	result = Own_Below_Threat() && (Cur_Vertical_Sep >= MINSEP) && (Down_Separation >= ALIM());
    }
    else
    {
	result = !(Own_Above_Threat()) || ((Own_Above_Threat()) && (Up_Separation > ALIM()));
    }
    return result;
}

bool Own_Below_Threat()
{
    return (Own_Tracked_Alt < Other_Tracked_Alt) && 1;
}

bool Own_Above_Threat()
{
    return (Other_Tracked_Alt < Own_Tracked_Alt) && 1;
}

int alt_sep_test()
{
    bool enabled, tcas_equipped, intent_not_known;
    bool need_upward_RA, need_downward_RA;
    int alt_sep;

    enabled = High_Confidence && (Own_Tracked_Alt_Rate <= OLEV) && (Cur_Vertical_Sep > MAXALTDIFF);
    tcas_equipped = Other_Capability == TCAS_TA && 1;
    intent_not_known = Two_of_Three_Reports_Valid && Other_RAC == NO_INTENT;
    
    alt_sep = UNRESOLVED;
    
    if (enabled && ((tcas_equipped && intent_not_known) || !tcas_equipped))
    {
	need_upward_RA = Non_Crossing_Biased_Climb() && Own_Below_Threat();
	need_downward_RA = Non_Crossing_Biased_Descend() && Own_Above_Threat();
	if (need_upward_RA && need_downward_RA)
        /* unreachable: requires Own_Below_Threat and Own_Above_Threat
           to both be true - that requires Own_Tracked_Alt < Other_Tracked_Alt
           and Other_Tracked_Alt < Own_Tracked_Alt, which isn't possible */
	    alt_sep = UNRESOLVED;
	else if (need_upward_RA)
	    alt_sep = UPWARD_RA;
	else if (need_downward_RA)
	    alt_sep = DOWNWARD_RA;
	else
	    alt_sep = UNRESOLVED;
    }
    
    return alt_sep;
}


//<ASSUME_CORRECT>

void initialize_correct()
{
    Positive_RA_Alt_Thresh[0] = 400;
    Positive_RA_Alt_Thresh[1] = 500;
    Positive_RA_Alt_Thresh[2] = 640;
    Positive_RA_Alt_Thresh[3] = 740;
}

int ALIM_correct ()
{
 return Positive_RA_Alt_Thresh[Alt_Layer_Value];
}

int Inhibit_Biased_Climb_correct ()
{
    return (Climb_Inhibit ? Up_Separation + NOZCROSS_correct : Up_Separation);
}

bool Non_Crossing_Biased_Climb_correct()
{
    int upward_preferred;
    int upward_crossing_situation;
    bool result;

    //upward_preferred = Inhibit_Biased_Climb_correct() > Down_Separation;
    if (Inhibit_Biased_Climb_correct() > Down_Separation)
    {
  result = !(Own_Below_Threat_correct()) || ((Own_Below_Threat_correct()) && (!(Down_Separation >= ALIM_correct())));
    }
    else
    {
  result = Own_Above_Threat_correct() && (Cur_Vertical_Sep >= MINSEP_correct) && (Up_Separation >= ALIM_correct());
    }
    return result;
}

bool Non_Crossing_Biased_Descend_correct()
{
    int upward_preferred;
    int upward_crossing_situation;
    bool result;

    //upward_preferred = Inhibit_Biased_Climb_correct() > Down_Separation;
    if (Inhibit_Biased_Climb_correct() > Down_Separation)
    {
  result = Own_Below_Threat_correct() && (Cur_Vertical_Sep >= MINSEP_correct) && (Down_Separation >= ALIM_correct());
    }
    else
    {
  result = !(Own_Above_Threat_correct()) || ((Own_Above_Threat_correct()) && (Up_Separation >= ALIM_correct()));
    }
    return result;
}

bool Own_Below_Threat_correct()
{
    return (Own_Tracked_Alt < Other_Tracked_Alt) && 1;
}

bool Own_Above_Threat_correct()
{
    return (Other_Tracked_Alt < Own_Tracked_Alt) && 1;
}

int alt_sep_test_correct()
{
    bool enabled, tcas_equipped, intent_not_known;
    bool need_upward_RA, need_downward_RA;
    int alt_sep;

    enabled = High_Confidence && (Own_Tracked_Alt_Rate <= OLEV_correct) && (Cur_Vertical_Sep > MAXALTDIFF_correct);
    tcas_equipped = Other_Capability == TCAS_TA_correct && 1;
    intent_not_known = Two_of_Three_Reports_Valid && Other_RAC == NO_INTENT_correct;

    alt_sep = UNRESOLVED_correct;

    if (enabled && ((tcas_equipped && intent_not_known) || !tcas_equipped))
    {
  need_upward_RA = Non_Crossing_Biased_Climb_correct() && Own_Below_Threat_correct();
  need_downward_RA = Non_Crossing_Biased_Descend_correct() && Own_Above_Threat_correct();
  if (need_upward_RA && need_downward_RA)
        /* unreachable: requires Own_Below_Threat and Own_Above_Threat
           to both be true - that requires Own_Tracked_Alt < Other_Tracked_Alt
           and Other_Tracked_Alt < Own_Tracked_Alt, which isn't possible */
      alt_sep = UNRESOLVED_correct;
  else if (need_upward_RA)
      alt_sep = UPWARD_RA_correct;
  else if (need_downward_RA)
      alt_sep = DOWNWARD_RA_correct;
  else
      alt_sep = UNRESOLVED_correct;
    }

    return alt_sep;
}

main(argc, argv)
int argc;
char *argv[];
{
    Cur_Vertical_Sep = nondet_int();// = atoi(argv[1]);
    High_Confidence = nondet_int();// = atoi(argv[2]);
    __CPROVER_assume(High_Confidence>=0 && High_Confidence<=1);
    Two_of_Three_Reports_Valid = nondet_int();// = atoi(argv[3]);
    __CPROVER_assume(Two_of_Three_Reports_Valid>=0 && Two_of_Three_Reports_Valid<=1);
    Own_Tracked_Alt = nondet_int();// = atoi(argv[4]);
    Own_Tracked_Alt_Rate = nondet_int();// = atoi(argv[5]);
    Other_Tracked_Alt = nondet_int();// = atoi(argv[6]);
    Alt_Layer_Value = nondet_int();// = atoi(argv[7]);
    __CPROVER_assume(Alt_Layer_Value>=0 && Alt_Layer_Value<=3);
    Up_Separation = nondet_int();// = atoi(argv[8]);
    Down_Separation = nondet_int();// = atoi(argv[9]);
    Other_RAC = nondet_int();// = atoi(argv[10]);
    __CPROVER_assume(Other_RAC>=0 && Other_RAC<=1);
    Other_Capability = nondet_int();// = atoi(argv[11]);
    __CPROVER_assume(Other_Capability>=0 && Other_Capability<=1);
    Climb_Inhibit = nondet_int();// = atoi(argv[12]);
    __CPROVER_assume(Climb_Inhibit>=0 && Climb_Inhibit<=1);
    __CPROVER_assume(Own_Tracked_Alt<=100000 && Other_Tracked_Alt<=100000 && Up_Separation<=100000 && Down_Separation<=100000 && Cur_Vertical_Sep<=100000 && Own_Tracked_Alt_Rate<=100000);
    //__CPROVER_assume(Own_Tracked_Alt>=0 && Other_Tracked_Alt>=0 && Up_Separation>=0 && Down_Separation>=0 && Cur_Vertical_Sep>=0 && Own_Tracked_Alt_Rate>=0);

    initialize();
    int res = alt_sep_test();
    initialize_correct();
    int res_correct = alt_sep_test_correct();
    assert(res == res_correct);
}
//</ASSUME_CORRECT>
