#!/usr/bin/env python
# =============================================================================
__author__ = " Alexander Mazurov alexander.mazurov@gmail.com"
__date__ = " 2012-06-18 "
__version__ = "$$Version$$"
# =============================================================================
# import everything from bender
from Bender.Main import *
from Gaudi.Configuration import *
from GaudiKernel.SystemOfUnits import MeV, GeV, mm
import BenderTools.TisTos
import BenderTools.Fill
# import sys
from IPython import embed as shell
# =============================================================================
# Simple class to look for Chi_b-peak
#  @author Vanya BELYAEV ibelyaev@physics.syr.edu
#  @date 2006-10-13


def _initialize(self):
    """
    Initialization
    """
    sc = Algo.initialize(self)
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
    # lines['Ups']['Hlt2TOS'] = 'Hlt2DiMuonHighMass.*Decision'
    lines['Ups']['Hlt2TOS'] = 'Hlt2(DiMuon|SingleMuonHighPT).*Decision'
    lines['Ups']['Hlt2TIS'] = ('Hlt2(Charm|Topo|Single|Express|Inc|Tri).'
                               '*Decision')

    sc = self.tisTos_initialize(triggers, lines)
    if sc.isFailure():
        return sc

    self.count = 0

    return SUCCESS


def _finalize(self):
    """
    Standard finalization
    """
    #
    # print "COUNT=%d" % self.count
    Algo.tisTos_finalize(self)
    return Algo.finalize(self)


class Chib(Algo):

    """
    Simple class to look for Chi_b-peak
    """
    # the standard initialization

    def initialize(self):
        return _initialize(self)

    # standard mehtod for analysis
    def analyse(self):
        """
        The standard method for analysis
        """
        # Primary vertices
        primaries = self.vselect('PVs', ISPRIMARY)
        if primaries.empty():
            return self.Warning('No primary vertices are found', SUCCESS)

        # rec summary
        rc_summary = self.get('/Event/Rec/Summary').summaryData()

        # select chib
        chibs = self.select(
            'dimion', 'Meson -> ( Meson -> mu+ mu- ) gamma')
        if chibs.empty():
            return self.Warning("No dimuons are found!", SUCCESS)

        # book n-=tuple
        tup = self.nTuple('Chib')

        chi2_dtf = DTF_CHI2NDOF(True)
        deltaM = DTF_FUN(M - M1, True)

        mups = DTF_FUN(M, True)
        minDLLmu = MINTREE(ISBASIC, PIDmu - PIDpi)
        kullback = MINTREE(ISBASIC & HASTRACK, CLONEDIST)

        max_tr_chi2_dof = MAXTREE(ISBASIC & HASTRACK, TRCHI2DOF)
        min_clonedist = MINTREE(ISBASIC & HASTRACK, CLONEDIST)
        vfaspf_vpchi2 = VFASPF(VPCHI2)
        abs_bpv_vz = BPV(VZ)
        vrho2 = VX ** 2 + VY ** 2
        bpv_vrho2 = BPV(vrho2)

        dm_1s_ = ADMASS('Upsilon(1S)')
        dm_2s_ = ADMASS('Upsilon(2S)')
        dm_3s_ = ADMASS('Upsilon(3S)')

        for chib in chibs:
            # shell()
            # delta mass

            ups = chib(1)
            gam = chib(2)

            if not ups:
                continue
            if not gam:
                continue

            mu1 = ups.child(1)
            mu2 = ups.child(2)

            if not (mu1 and mu2):
                continue
            dm = (M12(chib) - M1(chib)) / GeV
            if dm > 2:
                continue

            dm_1s = dm_1s_(ups) / GeV
            dm_2s = dm_2s_(ups) / GeV
            dm_3s = dm_3s_(ups) / GeV

            # if dm_1s > 0.2:
            #     continue

            pt_ups = PT(ups) / GeV
            # if pt_ups < 6:
            #     continue

            pt_g = PT(gam) / GeV
            # if pt_g < 0.6:
            #     continue

            c2_dtf_ups = chi2_dtf(ups)
            # if not 0 < c2_dtf_ups < 4:
            #     continue

            cl_g = CL(gam)
            # if cl_g < 0.01:
            #     continue

            lv01 = LV02(chib)
            # if lv01 < 0:
            #     continue

            dll_min = minDLLmu(ups)
            # if dll_min < 0:
            #     continue

            y = Y(ups)
            # if not 2 < y < 4.5:
            #     continue

            tup.column('dm', dm)
            tup.column('dmplusm1s', dm+9.46030)
            tup.column('dmplusm2s', dm+10.02326)
            tup.column('dmplusm3s', dm+10.3552)
            tup.column('m', M1(chib) / GeV)
            tup.column('pt_g', pt_g)
            tup.column('pt_ups', pt_ups)
            tup.column("y", y)
            tup.column('c2_dtf', c2_dtf_ups)
            tup.column('dm_1s', dm_1s)
            tup.column('dm_2s', dm_2s)
            tup.column('dm_3s', dm_3s)
            tup.column('dll_min', dll_min)
            tup.column("y_chib", Y(chib))

            tup.column("lv01", lv01)
            tup.column("chi2_vx", VCHI2(ups.endVertex()))

            tup.column('mu_dtf', mups(ups) / GeV)
            tup.column('m_dtf', mups(chib) / GeV)
            tup.column('dm_dtf', deltaM(chib) / GeV)

            tup.column('pt_chib', PT(chib) / GeV)
            tup.column('cl_g', cl_g)

            # pi0veto = LoKi.Photons.pi0Veto ( gam , allg , 25 * MeV , -1 )
            # tup.column ( 'pi0veto'  , pi0veto , 0 , 1 )

            tup.column('p_mu1', P(mu1) / GeV)
            tup.column('p_mu2', P(mu2) / GeV)
            tup.column('pt_mu1', PT(mu1) / GeV)
            tup.column('pt_mu2', PT(mu2) / GeV)

            tup.column('probnn_mu1', PROBNNmu(mu1))
            tup.column('probnn_mu2', PROBNNmu(mu2))

            tup.column('kl_dist', kullback(ups))
            tup.column('max_tr_chi2_dof', max_tr_chi2_dof(ups))
            tup.column('min_clonedist', min_clonedist(ups))
            tup.column('vfaspf_vpchi2', vfaspf_vpchi2(ups))
            tup.column('abs_bpv_vz', abs_bpv_vz(ups))
            tup.column('bpv_vrho2', bpv_vrho2(ups))

            # fill TisTos info
            self.tisTos(ups,
                        tup,
                        'Ups_',
                        self.lines['Ups'], verbose=True)

            # add some reco-summary information
            self.addRecSummary(tup, rc_summary)

            tup.write()
            # chib.save ( 'chib' )

        ok = self.selected('chib')
        self.setFilterPassed(0 < len(ok))
        return SUCCESS

    # finalization
    def finalize(self):
        return _finalize(self)


class Upsilon(Algo):

    """
    Simple class to look for Chi_b-peak
    """
    # the standard initialization

    def initialize(self):
        return _initialize(self)

    # standard mehtod for analysis
    def analyse(self):
        """
        The standard method for analysis
        """

        # select dimuons
        dimuons = self.select('dimuon', 'Meson -> mu+ mu-')
        if dimuons.empty():
            return self.Warning("No dimuons are found!", SUCCESS)

        # Primary vertices
        primaries = self.vselect('PVs', ISPRIMARY)
        if primaries.empty():
            return self.Warning('No primary vertices are found', SUCCESS)

        # rec summary
        rc_summary = self.get('/Event/Rec/Summary').summaryData()
        # select heavy dimuons
        upsilons = self.select('ups',
                               dimuons,
                              (8 * GeV <= M) & (M < 12 * GeV))
        if upsilons.empty():
            return self.Warning("No heavy dimuons  are found!", SUCCESS)

        # =====================================================================
        chi2_dtf = DTF_CHI2NDOF(True)
        # deltaM = DTF_FUN(M - M1, True)
        mups = DTF_FUN(M, True)
        minDLLmu = MINTREE(ISBASIC, PIDmu - PIDpi)
        kullback = MINTREE(ISBASIC & HASTRACK, CLONEDIST)

        dm_1s = ADMASS('Upsilon(1S)')
        dm_2s = ADMASS('Upsilon(2S)')
        dm_3s = ADMASS('Upsilon(3S)')
        # =====================================================================
        tup = self.nTuple('Upsilon')
        # collect TisTos-statistics
        # =====================================================================
        # Loop:
        # =====================================================================
        for ups in upsilons:
            # =================================================================
            self.decisions(ups, self.triggers['Ups'])
            # =================================================================
            mu1 = ups.child(1)
            mu2 = ups.child(2)
            # =================================================================
            if not (mu1 and mu2):
                continue
            # =================================================================
            m = M(ups) / GeV
            if not 8.5 < m < 12:
                continue

            pt_ups = PT(ups) / GeV
            # if not pt_ups > 6:
            #     continue

            c2_dtf = chi2_dtf(ups)
            # if not 0 < c2_dtf < 4:
            #     continue

            dll_min = minDLLmu(ups)
            # if dll_min < 0:
            #     continue

            y = Y(ups)
            # if not 2 < y < 4.5:
            #     continue

            # tup.column ( 'dm'     , dm           / GeV )
            tup.column('m', m)
            tup.column('c2_dtf', c2_dtf)
            tup.column('m_dtf', mups(ups) / GeV)

            tup.column('pt_ups', pt_ups)
            tup.column('p_mu1', P(mu1) / GeV)
            tup.column('p_mu2', P(mu2) / GeV)
            tup.column('pt_mu1', PT(mu1) / GeV)
            tup.column('pt_mu2', PT(mu2) / GeV)

            tup.column('probnn_mu1', PROBNNmu(mu1))
            tup.column('probnn_mu2', PROBNNmu(mu2))

            tup.column('dm_1s', dm_1s(ups) / GeV)
            tup.column('dm_2s', dm_2s(ups) / GeV)
            tup.column('dm_3s', dm_3s(ups) / GeV)

            tup.column('dll_min', dll_min)
            tup.column('kl_dist', kullback(ups))
            tup.column("y", y)

            # fill TisTos info
            self.tisTos(ups,
                        tup,
                        'Ups_',
                        self.lines['Ups'], verbose=True)

            # add some reco-summary information
            self.addRecSummary(tup, rc_summary)

            tup.write()

            # =================================================================
            # self.count += 1
            # if (self.count % 10) == 0:
            #     self.Warning ( "Upsilons %d" % self.count, SUCCESS)
            # =================================================================

        return SUCCESS

    # finalization
    def finalize(self):
        return _finalize(self)


# =============================================================================
# configure the job


def configure(datafiles, catalogs=[], castor=True, params={}):
    """
    Configure the job
    """

    from Configurables import DaVinci  # needed for job configuration
    from Configurables import EventSelector  # needed for job configuration
    from Configurables import NTupleSvc

    from PhysConf.Filters import LoKi_Filters

    fltrs = LoKi_Filters(
        STRIP_Code="""
        HLT_PASS_RE ( 'Stripping.*DiMuonHighMass.*Decision' )
        """,
        VOID_Code="""
        0 < CONTAINS (
            '/Event/Dimuon/Phys/FullDSTDiMuonDiMuonHighMassLine/Particles')
        """
    )

    filters = fltrs.filters('Filters')
    filters.reverse()

    the_year = params["year"]

    davinci = DaVinci(  # noqa
        DataType=the_year,
        InputType='MDST',
        HistogramFile="chib_histos.root",
        TupleFile="chib_tuples.root",
        PrintFreq=1000,
        Lumi=True,
        EvtMax=-1
    )
    from Configurables import CondDB
    CondDB(LatestGlobalTagByDataType=the_year)

    #=========================================================================
    # RootInTES = '/Event/ChiB'
    # RootInTES = '/Event/Bottomonia'
    RootInTES = '/Event/BOTTOM'
    #=========================================================================
    from BenderTools.MicroDST import uDstConf
    uDstConf(RootInTES)
    # =========================================================================
    from Configurables import Gaudi__IODataManager as IODataManager
    IODataManager().AgeLimit = 2
    # =========================================================================
    # come back to Bender
    setData(datafiles, catalogs, castor)
    gaudi = appMgr()
    alg_chib = Chib(
        'ChibAlg',  # Algorithm name ,
        # input particles
        RootInTES=RootInTES,
        Inputs=[
            # 'Phys/Chi_b/Particles'
            'Phys/ChiB/Particles'
        ],
        # take care about the proper particle combiner
        ParticleCombiners={'': 'LoKi::VertexFitter'}
    )
    alg_upsilon = Upsilon(
        'UpsilonAlg',  # Algorithm name ,
        # input particles
        RootInTES=RootInTES,
        Inputs=[
            'Phys/Upsilon/Particles'
        ],
        # take care about the proper particle combiner
        ParticleCombiners={'': 'LoKi::VertexFitter'}
    )
    # =========================================================================
    mainSeq = gaudi.algorithm('GaudiSequencer/DaVinciUserSequence', True)
    mainSeq.Members += [alg_chib.name(), alg_upsilon.name()]
    # =========================================================================
    return SUCCESS

# =============================================================================
# The actual job steering


def main():

    # make printout of the own documentations
    print '*' * 120
    print __doc__
    print ' Author  : %s ' % __author__
    print ' Version : %s ' % __version__
    print ' Date    : %s ' % __date__
    print '*' * 120

    # db = shelve.open("data/data_db","r")
    # configure ( db["chi_down"] , castor = True, skip=skip,step=step )
    # db = shelve.open("/afs/cern.ch/user/i/ibelyaev/public/LFNs/lfns.db", "r")
    # configure(db["DiMuon.Y&ChiB.Stripping17;Down"][2:3], castor=True)
    files = [
        '/lhcb/LHCb/Collision11/BOTTOM.MDST/00024290/0000/00024290_00000054_1.bottom.mdst',
        '/lhcb/LHCb/Collision11/BOTTOM.MDST/00024290/0000/00024290_00000031_1.bottom.mdst',
        '/lhcb/LHCb/Collision11/BOTTOM.MDST/00024290/0000/00024290_00000027_1.bottom.mdst',
        '/lhcb/LHCb/Collision11/BOTTOM.MDST/00024290/0000/00024290_00000016_1.bottom.mdst'
    ]
    configure(files, castor=True, params={"year": "2011"})
    run(1000)


if '__main__' == __name__:
    main()
# =============================================================================
# The END
# =============================================================================
