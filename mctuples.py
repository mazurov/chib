#!/usr/bin/env python
# =============================================================================
__author__ = " Alexander Mazurov alexander.mazurov@gmail.com"
__date__ = " 2012-06-18 "
__version__ = " Version $$"
# =============================================================================
# Preocess the file with Chi_b{NB}({NP})
# =============================================================================
# import everything from bender
from Bender.MainMC import *
from GaudiKernel.SystemOfUnits import GeV
import BenderTools.TisTosMC
# from IPython import embed as shell
# =============================================================================
# Simple class to look for Chi_b-peak
#  @author Vanya BELYAEV ibelyaev@physics.syr.edu
#  @date 2006-10-13


def _initialize(self):
    """
    Initialization
    """
    sc = AlgoMC.initialize(self)
    if sc.isFailure():
        return sc

    triggers = {}
    triggers['Ups'] = {}

    lines = {}
    lines['Ups'] = {}
    lines['Ups']['L0TOS'] = 'L0DiMuon.*Decision'
    lines['Ups'][
        'L0TIS'] = 'L0(Hadron|Muon|DiMuon|Photon|Electron)Decision'
    lines['Ups']['Hlt1TOS'] = 'Hlt1DiMuonHighMass.*Decision'
    lines['Ups']['Hlt1TIS'] = 'Hlt1TrackAll.*Decision'
    lines['Ups']['Hlt2TOS'] = 'Hlt2(DiMuon|SingleMuonHighPT).*Decision'
    lines['Ups']['Hlt2TIS'] = ('Hlt2(Charm|Topo|Single|Express|Inc|Tri).'
                               '*Decision')

    sc = self.tisTos_initialize(triggers, lines)
    if sc.isFailure():
        return sc

    self.count = 0

    return SUCCESS

# finalization


def _finalize(self):
    """
    Standard finalization
    """
    #
    self.tisTos_finalize(self)
    return AlgoMC.finalize(self)


class ChibMC(AlgoMC):

    """
    Simple class to look for Chi_b-peak
    """
    # the standard initialization
    def initialize(self):
        return _initialize(self)

    # standard mehtod for analysis
    # standard mehtod for analysis
    def analyse(self):
        """
        The standard method for analysis
        """

        # select chib
        chibs = self.select(
            'dimion', 'Meson -> (Meson -> mu+ mu- ) gamma')

        if chibs.empty():
            return self.Warning("No dimuons are found!", SUCCESS)

        #
        # check MC, In MC 2P and 3P - are defined as 1P with mass redifinition
        real_chib_name = "chi_b{nb}({np}P)".format(nb=self.nb, np=self.np)
        mc_chib_name = "chi_b{nb}(1P)".format(nb=self.nb)

        cb = self.mcselect('chib_ups1s',
            '%s ->  ( Upsilon(1S) => mu+ mu- )  gamma' % mc_chib_name)
        cb_y = self.mcselect('chib_ups1s_y',
            '%s ->  ^( Upsilon(1S) => mu+ mu- )  gamma' % mc_chib_name)
        cb_g = self.mcselect('chib_ups1s_g',
            '%s ->  ( Upsilon(1S) => mu+ mu- )  ^gamma' % mc_chib_name)

        if cb.empty() or cb_y.empty() or cb_g.empty():
            return self.Warning('No true MC-decays are found', SUCCESS)

        mc_cb = NONE if cb.empty() else MCTRUTH(cb, self.mcTruth())
        mc_cb_y = NONE if cb_y.empty() else MCTRUTH(cb_y, self.mcTruth())
        mc_cb_g = NONE if cb_g.empty() else MCTRUTH(cb_g, self.mcTruth())

        # book n-=tuple
        tup = self.nTuple('Chib')

        chi2_dtf = DTF_CHI2NDOF(True)
        deltaM = DTF_FUN(M - M1, True)

        mups = DTF_FUN(M, True)
        minDLLmu = MINTREE(ISBASIC, PIDmu - PIDpi)
        kullback = MINTREE(ISBASIC & HASTRACK, CLONEDIST)

        dm_1s = ADMASS('Upsilon(1S)')
        dm_2s = ADMASS('Upsilon(2S)')
        dm_3s = ADMASS('Upsilon(3S)')

        matched_count = 0

        for chib in chibs:
            # delta mass
            dm = (M12(chib) - M1(chib)) / GeV
            if dm > 2:
                continue

            ups = chib(1)
            gam = chib(2)

            if not (ups or gam):
                continue

            mu1 = ups.child(1)
            mu2 = ups.child(2)

            if not (mu1 or mu2):
                continue

            pt_ups = PT(ups) / GeV
            pt_g = PT(gam) / GeV
            y_ups = Y(ups)
            c2_dtf = chi2_dtf(ups)
            lv01 = LV02(chib)
            dll_min = minDLLmu(ups)

            tup.column('dm', dm)
            tup.column('m', M1(chib) / GeV)
            tup.column('pt_ups', pt_ups)
            tup.column('pt_g', pt_g)
            tup.column("y", y_ups)
            tup.column("y_chib", Y(chib))
            tup.column('c2_dtf', c2_dtf)

            tup.column('cl_g', CL(gam))
            tup.column('dll_min', dll_min)

            tup.column("chi2_vx", VCHI2(ups.endVertex()))
            tup.column("lv01", lv01)

            tup.column('mu_dtf', mups(ups) / GeV)
            tup.column('m_dtf', mups(chib) / GeV)
            tup.column('dm_dtf', deltaM(chib) / GeV)

            tup.column('pt_chib', PT(chib) / GeV)

            tup.column('p_mu1', P(mu1) / GeV)
            tup.column('p_mu2', P(mu2) / GeV)
            tup.column('pt_mu1', PT(mu1) / GeV)
            tup.column('pt_mu2', PT(mu2) / GeV)

            tup.column('dm_1s', dm_1s(ups) / GeV)
            tup.column('dm_2s', dm_2s(ups) / GeV)
            tup.column('dm_3s', dm_3s(ups) / GeV)

            tup.column('kl_dist', kullback(ups))

            tup.column('e_g', E(gam) / GeV)
            tup.column('e_y', E(ups) / GeV)
            tup.column('px_g', PX(gam) / GeV)
            tup.column('px_y', PX(ups) / GeV)
            tup.column('py_g', PY(gam) / GeV)
            tup.column('py_y', PY(ups) / GeV)
            tup.column('pz_g', PZ(gam) / GeV)
            tup.column('pz_y', PZ(ups) / GeV)

            # fill TisTos info
            self.tisTos(ups, tup, 'Ups_', self.lines['Ups'])

            # -----------------------------------------------------------------
            # MC
            # -----------------------------------------------------------------
            tup.column('true_cb_ups1s', mc_cb(chib))
            tup.column('true_cb_ups1s_y', mc_cb_y(ups))
            tup.column('true_cb_ups1s_g', mc_cb_g(gam))

            tup.column('mc_cb_y_e', -1 if cb_y.empty() else MCE(cb_y(0)) / GeV)
            tup.column('mc_cb_g_e', -1 if cb_g.empty() else MCE(cb_g(0)) / GeV)

            tup.column('mc_cb_y_pt', -1 if cb_y.empty() else MCPT(cb_y(0)) / GeV)
            tup.column('mc_cb_g_pt', -1 if cb_g.empty() else MCPT(cb_g(0)) / GeV)

            tup.column('mc_cb_y_px', -1 if cb_y.empty() else MCPX(cb_y(0)) / GeV)
            tup.column('mc_cb_g_px', -1 if cb_g.empty() else MCPX(cb_g(0)) / GeV)

            tup.column('mc_cb_y_py', -1 if cb_y.empty() else MCPY(cb_y(0)) / GeV)
            tup.column('mc_cb_g_py', -1 if cb_g.empty() else MCPY(cb_g(0)) / GeV)

            tup.column('mc_cb_y_pz', -1 if cb_y.empty() else MCPZ(cb_y(0)) / GeV)
            tup.column('mc_cb_g_pz', -1 if cb_g.empty() else MCPZ(cb_g(0)) / GeV)
            # -----------------------------------------------------------------
            tup.column('nb', self.nb)
            tup.column('np', self.np)
            tup.write()
            # -----------------------------------------------------------------
            # end for cycle
            # -----------------------------------------------------------------

        if matched_count > 1:
            self.plot(matched_count, "Matched %s per event" %
                      real_chib_name, -0.5, 5.5, 6)

        ok = self.selected('chib')
        self.setFilterPassed(0 < len(ok))
        return SUCCESS

    # finalization
    def finalize(self):
        return _finalize(self)


class UpsilonMC(AlgoMC):

    """
    Simple class to look for Chi_b-peak
    """
    # the standard initialization
    def initialize(self):
        return _initialize(self)

    # standard mehtod for analysis
    # standard mehtod for analysis
    def analyse(self):
        """
        The standard method for analysis
        """
        # select chib
        upsilons = self.select(
            'dimion', 'Meson -> mu+ mu-')

        if upsilons.empty():
            return self.Warning("No dimuons are found!", SUCCESS)

        #
       # check MC, In MC 2P and 3P - are defined as 1P with mass redifinition
        mups = []
        for s in range(1, 4):
            mups.append(self.mcselect(
                'ups%ds' % s,
                'chi_b{nb}(1P) -> ^(Upsilon({s}S) => mu+ mu- ) gamma'
                .format(nb=self.nb, s=s))
            )

        if mups[0].empty() and mups[1].empty() and mups[2].empty():
            self.Warning('No true MC-decays are found')

        mc_ups = []
        for mupsilon in mups:
            mc_ups.append(NONE if mupsilon.empty() else
                          MCTRUTH(mupsilon, self.mcTruth()))

        # book n-=tuple
        tup = self.nTuple('Upsilon')

        chi2_dtf = DTF_CHI2NDOF(True)
        mups = DTF_FUN(M, True)
        minDLLmu = MINTREE(ISBASIC, PIDmu - PIDpi)
        kullback = MINTREE(ISBASIC & HASTRACK, CLONEDIST)

        dm_1s = ADMASS('Upsilon(1S)')
        dm_2s = ADMASS('Upsilon(2S)')
        dm_3s = ADMASS('Upsilon(3S)')

        matched_count = 0
        for ups in upsilons:
            m = M(ups) / GeV
            if not 8.5 < m < 12:
                continue

            pt_ups = PT(ups) / GeV
            c2_dtf = chi2_dtf(ups)
            y_ups = Y(ups)
            # =================================================================
            mu1 = ups.child(1)
            mu2 = ups.child(2)
            if not (mu1 or mu2):
                continue
            # =================================================================
            # tup.column ( 'dm'     , dm           / GeV )
            tup.column('m', m)
            tup.column('pt_ups', pt_ups)
            tup.column('c2_dtf', c2_dtf)
            tup.column("y", y_ups)
            tup.column('dll_min', minDLLmu(ups))

            tup.column('m_dtf', mups(ups) / GeV)
            tup.column('p_mu1', P(mu1) / GeV)
            tup.column('p_mu2', P(mu2) / GeV)
            tup.column('pt_mu1', PT(mu1) / GeV)
            tup.column('pt_mu2', PT(mu2) / GeV)

            tup.column('dm_1s', dm_1s(ups) / GeV)
            tup.column('dm_2s', dm_2s(ups) / GeV)
            tup.column('dm_3s', dm_3s(ups) / GeV)

            tup.column('kl_dist', kullback(ups))

            # fill TisTos info
            self.tisTos(ups,
                        tup,
                        'Ups_',
                        self.lines['Ups'])

            for i in range(3):
                true_y = mc_ups[i](ups)
                tup.column('true_y%ds' % (i + 1), true_y)
                if true_y:
                    matched_count += 1

            tup.column('nb', self.nb)
            tup.column('np', self.np)
            tup.write()

        real_chib_name = "chi_b{nb}({np}P)".format(nb=self.nb, np=self.np)
        if matched_count > 1:
            self.plot(matched_count, "Matched Upsilons per event (%s)" %
                      real_chib_name, -0.5, 5.5, 6)

        ok = self.selected('ups')
        self.setFilterPassed(0 < len(ok))
        return SUCCESS

    # finalization
    def finalize(self):
        return _finalize(self)

# =============================================================================
# configure the job


def configure(datafiles, catalogs=[], castor=True, params=None):
    """
    Configure the job
    """

    from Configurables import DaVinci  # needed for job configuration
    # from Configurables import EventSelector  # needed for job configuration
    # from Configurables import NTupleSvc

    from PhysConf.Filters import LoKi_Filters

    fltrs = LoKi_Filters(
        STRIP_Code="""
        HLT_PASS_RE ( 'Stripping.*DiMuonHighMass.*Decision' )
        """,
        VOID_Code="""
        0 < CONTAINS (
            '/Event/AllStreams/Phys/FullDSTDiMuonDiMuonHighMassLine/Particles')
        """
    )

    filters = fltrs.filters('Filters')
    filters.reverse()

    from PhysSelPython.Wrappers import AutomaticData, Selection, SelectionSequence

    #
    # defimuon in stripping DST
    #
    # DiMuLocation  =
    # '/Event/Dimuon/Phys/FullDSTDiMuonDiMuonHighMassLine/Particles'
    DiMuLocation = '/Event/AllStreams/Phys/FullDSTDiMuonDiMuonHighMassLine/Particles'

    from PhysSelPython.Wrappers import AutomaticData
    DiMuData = AutomaticData(Location=DiMuLocation)

    # =========================================================================
    # Upsilon -> mumu, cuts by  Giulia Manca
    # ========================================================================
    from GaudiConfUtils.ConfigurableGenerators import FilterDesktop
    UpsAlg = FilterDesktop(
        Code="""
        ( M > 7 * GeV ) &
        DECTREE   ('Meson -> mu+ mu-'  )                      &
        CHILDCUT( 1 , HASMUON & ISMUON )                      &
        CHILDCUT( 2 , HASMUON & ISMUON )                      &
        ( MINTREE ( 'mu+' == ABSID , PT ) > 1 * GeV         ) &
        ( MAXTREE ( ISBASIC & HASTRACK , TRCHI2DOF ) < 4    ) &
        ( MINTREE ( ISBASIC & HASTRACK , CLONEDIST ) > 5000 ) &
        ( VFASPF  ( VPCHI2 ) > 0.5/100 )
        & ( abs ( BPV ( VZ    ) ) <  0.5 * meter     )
        & (       BPV ( vrho2 )   < ( 10 * mm ) ** 2 )
        """,
        Preambulo=[
            "vrho2 = VX**2 + VY**2"
        ],
        ReFitPVs=True
    )

    UpsSel = Selection(
        'UpsSel',
        Algorithm=UpsAlg,
        RequiredSelections=[DiMuData]
    )

    # =========================================================================
    # chi_b -> Upsilon gamma
    # ========================================================================
    from GaudiConfUtils.ConfigurableGenerators import CombineParticles
    ChibCombine = CombineParticles(
        DecayDescriptor="chi_b1(1P) ->  J/psi(1S) gamma",
        DaughtersCuts={
            "gamma": " ( 350 * MeV < PT ) & ( CL > 0.01 )  "
        },
        CombinationCut="""
        ( AM - AM1 ) < 3 * GeV
        """,
        MotherCut=" PALL",
        #
        # we are dealing with photons!
        #
        ParticleCombiners={
        '': 'LoKi::VertexFitter'
        }
    )
    from StandardParticles import StdLooseAllPhotons  # needed for chi_b
    ChibSel1 = Selection(
        'PreSelChib',
        Algorithm=ChibCombine,
        RequiredSelections=[UpsSel, StdLooseAllPhotons]
    )
    from GaudiConfUtils.ConfigurableGenerators import Pi0Veto__Tagger
    TagAlg = Pi0Veto__Tagger(
        ExtraInfoIndex=25001,  # should be unique!
        MassWindow=20 * MeV,  # cut on delta-mass
        MassChi2=-1,  # no cut for chi2(mass)
    )
    ChibSel2 = Selection(
        'Chi_b',
        Algorithm=TagAlg,
        RequiredSelections=[ChibSel1]
    )
    Chib = SelectionSequence("ChiB", TopSelection=ChibSel2)

    # print 'OUTPUT!!!' , output_loc

    # =========================================================================
    # Upsilons
    # ========================================================================
    Ups = SelectionSequence("UpsSelSeq", TopSelection=UpsSel)
    # ========================================================================
    from Configurables import GaudiSequencer
    myChibSeq = GaudiSequencer('MyChibSeq')
    myChibSeq.Members = [Chib.sequence()] + ["ChibAlg"]

    myUpsSeq = GaudiSequencer('MyUpsSeq')
    myUpsSeq.Members = [Ups.sequence()] + ["UpsilonAlg"]

    davinci = DaVinci(
        EventPreFilters=filters,
        DataType='2011',
        Simulation=True,
        InputType='DST',
        HistogramFile="chib_histos.root",
        TupleFile="chib_tuples.root",
        PrintFreq=1000,
        Lumi=True,
        EvtMax=-1
    )

    davinci.UserAlgorithms = [myChibSeq, myUpsSeq]

    # =========================================================================
    from Configurables import Gaudi__IODataManager as IODataManager
    IODataManager().AgeLimit = 2
    # =========================================================================
    # come back to Bender
    setData(datafiles, catalogs, castor)
    gaudi = appMgr()

    alg_chib = ChibMC(
        'ChibAlg',  # Algorithm name ,
        # input particles
        Inputs=[
            Chib.outputLocation()
        ],
        # take care about the proper particle combiner
        ParticleCombiners={'': 'LoKi::VertexFitter'}
    )

    alg_ups = UpsilonMC(
        'UpsilonAlg',  # Algorithm name ,
        # input particles
        Inputs=[
            Ups.outputLocation()
        ],
        # take care about the proper particle combiner
        ParticleCombiners={'': 'LoKi::VertexFitter'}
    )

    alg_chib.nb = alg_ups.nb = params['nb']
    alg_chib.np = alg_ups.np = params['np']

    # =========================================================================
    return SUCCESS

# =============================================================================
# The actual job steering


def main():
    from ext.blessings import Terminal
    t = Terminal()
    # make printout of the own documentations
    print '*' * 120
    print __doc__
    print ' Author  : %s ' % __author__
    print ' Version : %s ' % __version__
    print t.green('*' * 120)

    prefix = "/lhcb/MC/MC11a/ALLSTREAMS.DST/"
    test_files = {
        "chib1(1P)": [
            "00021993/0000/00021993_00000001_1.allstreams.dst",
            "00021993/0000/00021993_00000002_1.allstreams.dst",
            "00021993/0000/00021993_00000003_1.allstreams.dst",
            "00021993/0000/00021993_00000004_1.allstreams.dst",
            "00021993/0000/00021993_00000005_1.allstreams.dst"
        ],
        "chib2(1P)": [
            "00022011/0000/00022011_00000001_1.allstreams.dst",
            "00022011/0000/00022011_00000002_1.allstreams.dst",
            "00022011/0000/00022011_00000003_1.allstreams.dst",
            "00022011/0000/00022011_00000004_1.allstreams.dst",
            "00022011/0000/00022011_00000005_1.allstreams.dst"
        ],
        "chib2(3P)": [
            "00022002/0000/00022002_00000001_1.allstreams.dst",
            "00022002/0000/00022002_00000002_1.allstreams.dst",
            "00022002/0000/00022002_00000003_1.allstreams.dst",
            "00022002/0000/00022002_00000004_1.allstreams.dst"
        ]
    }

    nb = 1
    np = 1
    chib_name = "chib%d(%dP)" % (nb, np)

    print t.green("Processing files for MC %s" % chib_name)
    print t.green('*' * 120)

    configure([prefix + file for file in test_files[chib_name]],
              castor=True,
              params={"nb": nb, "np": np})
    run(30000)


if '__main__' == __name__:
    main()
# =============================================================================
# The END
# =============================================================================