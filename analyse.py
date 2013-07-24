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
            tup.column('pz_g', PY(gam) / GeV)
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
