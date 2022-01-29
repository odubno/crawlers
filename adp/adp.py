import requests
import json
import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class ADPCrawler:

    """
    AudioEye is definitely doing some type of cookie monitoring here:
        '// AudioEye is actively monitoring this site'
        i.e. https://wsv3cdn.audioeye.com/frame/cookieStorage.html?build=prod&pscb=
        There must be a javascript used to generate some of the cookies
    Using requests
        Cookies are being generated using js and at this moment I do not want to spend more time figuring this out
    Using Selenium
        ADP is pretty good at catching selenium and raising "Application Error. Please try again Later[]"
        It's tough. I think introducing human typing could help by pass this.
    """

    def __init__(self, username, password):
        self.session = requests.session()
        self.username = username
        self.password = password
        # initialize common browser objects; finger_print and user_agent do not have to change
        self.finger_print = "version%3D3%2E5%2E0%5F1%26pm%5Ffpua%3Dmozilla%2F5%2E0%20%28macintosh%3B%20intel%20mac%20os%20x%2010%5F15%5F7%29%20applewebkit%2F537%2E36%20%28khtml%2C%20like%20gecko%29%20chrome%2F97%2E0%2E4692%2E71%20safari%2F537%2E36%7C5%2E0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010%5F15%5F7%29%20AppleWebKit%2F537%2E36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F97%2E0%2E4692%2E71%20Safari%2F537%2E36%7CMacIntel%26pm%5Ffpsc%3D30%7C1512%7C982%7C944%26pm%5Ffpsw%3D%26pm%5Ffptz%3D%2D5%26pm%5Ffpln%3Dlang%3Den%2DUS%7Csyslang%3D%7Cuserlang%3D%26pm%5Ffpjv%3D0%26pm%5Ffpco%3D1%26pm%5Ffpasw%3Dinternal%2Dpdf%2Dviewer%7Cinternal%2Dpdf%2Dviewer%7Cinternal%2Dpdf%2Dviewer%7Cinternal%2Dpdf%2Dviewer%7Cinternal%2Dpdf%2Dviewer%26pm%5Ffpan%3DNetscape%26pm%5Ffpacn%3DMozilla%26pm%5Ffpol%3Dtrue%26pm%5Ffposp%3D%26pm%5Ffpup%3D%26pm%5Ffpsaw%3D1512%26pm%5Ffpspd%3D30%26pm%5Ffpsbd%3D%26pm%5Ffpsdx%3D%26pm%5Ffpsdy%3D%26pm%5Ffpslx%3D%26pm%5Ffpsly%3D%26pm%5Ffpsfse%3D%26pm%5Ffpsui%3D%26pm%5Fos%3DMac%26pm%5Fbrmjv%3D97%26pm%5Fbr%3DChrome%26pm%5Finpt%3D%26pm%5Fexpt%3D"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        # product id is a hardcoded id to identify ADP's payroll product
        self.product_id = "80e309c3-70c6-bae1-e053-3505430b5495"
        # xsrf and session tokens will vary for each session
        self.xsrf_token = ""
        self.adp_session = ""

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def handle_login_cookies(self):
        # handle login and load cookies by making preliminary requests
        login_url = "https://my.adp.com/"
        _ = self.get(login_url)
        _ = self.get("https://online.adp.com/csrf")

    def handle_signin_start(self):
        # xsrf is used as part of the headers
        self.xsrf_token = self.session.cookies.get("XSRF-TOKEN")
        headers = {
            "Content-Type": "application/json",
            "X-XSRF-TOKEN": self.xsrf_token,
        }
        data = {"productId": self.product_id, "organizationId": ""}
        sign_in_start = self.post(
            "https://online.adp.com/api/sign-in-service/v1/sign-in.start",
            data=json.dumps(data),
            headers=headers,
        )
        self.adp_session = sign_in_start.json()["session"]

    def handle_signin_username(self):
        # submit username
        data = {"identifier": self.username, "session": self.adp_session}
        # below cookies are generated using JS (likely monitored by AudioEye)
        # It'll take days of effort to work on executing JS to get these right; but not impossible
        x_a = "CC2LOJT3KZ0a4TIJa3z5k_M-fR8p-MXmiHwAEhfdsxvkyLTGIkTLz1Frb=MGor=zTnwORTKBGT8bMLEXX9VXZ8p=t6ZBSrHRNnXwE90aKLTc=kJuO3TE9OkfQbtCv1qa6XEBAZwmicl2CTXLXj7uc2G7tpcrELwrwNRC9Lys46PLgNKEiZpi4sloKG7raxEUsDaolc35p_qnTAw-UeYM7KKkiwVoq6ZYXky=anLAoAmMRsJM096S6Ab9d=XkgZaDDwuTvi40GtHfR_--mDz95GgAHu4wnLwCCCza7kXj1XhEjg-PyFwXIqkPIIEAqboXkgVFfOo2Js5jC0NQVQk=_CGe7BKQoMLc2bp4JNeqG2BIRiTZRYEzQF9bxJ3pCnZ7czhcmQM0hb8KJdpa4u7vCS8IRZgT9wx-4R-wTLTRzYCz-KpXJPwf6vacltHBSvpulRembsR-3ZLDsnLdzCra_eqcbEp2Uzuy0NbrV0-OCmoGrmqTPNq=smnepxUADSwMMGGVAsUdkEh2vgiEIE8GBijV07mgMUaqB36YtAzoHCKqx5aylr4Oi_XVr20YR9OObZU51KLCDgqhyvBqYycGSqX5T1Uw5T4HS2Xm4aC_gosxdAjSDlJcviO0TMl0bFNqXvsnG6Z6ne-2hd4Jg6CLw-ydptxcpFvE_ybKDhfYZlpQgo-5MxY1t3ZJSfJnVy9xiRVtT_6TZL0P_xQfsFi-Ta5LGtOYwA_H8MqYObCAzo7UjTIgwyHchxIKKTdCCNz1_3FyxIdfvUJcijLNy4DeMYZmtR13XKBNDnN3=25TQiSbfL95u-y5RmcFvKjLwk9KhXzazDwQMKguOh5qPnMJO7QIQ2RqyUVu3TvcCwtFsS5ahhjUpuPsn--2=OQkVeagd--0tyY4x6Q_sa57cmhrDkajkkroVJyQzO=nHqd5KQsUwxa3vzYeXu-OGb6V9=Ipz6S5G=zM-Ct64r1GPu_h5bziRr6X2jgRXD9-1=H3e5dZyaXHtJhCHMNUEyQZ6-FG9cnc7Iu7msgzq8ahtGhCmh2dy4vLFfrtH1F4=AIZdf2SwMQ=0n-h2tNrs3uX22VX7ORBkDLmK__2uBywj9G69AU5qw=P5Ik9SqDfx0SqvX=DaODSiSFKDGBfQ182bhMNLdg6YbI5V5BF2wKFOeVf8HIcS=fIrEQVgBvglQxFl7D8aJXzuZH7Eq7n_spoFrRLT0Vea6_VmJ60EjYlZ=tBc=QihkXKtJfY8R5Hc9lNPOSf=kR0DE84hYHTwEUoBr33Rc6Swkqouck08AkMSANe=tcrD7dCQOOddxc0NIQG0hVoJmIr_rp9ECU6X6ap75hr4E2lkmvOP7v4t81Uuq5450zmBez_Askxyl_1oO9p0izdujNDV1S4htJFh31t8AmtidC50Lc3Q1e76ba5829JbFJXKHxOZAkBh7FcCO0O6aVRyUHkjL_Jqkw4uQi2kP_JM9S1UmDMMXmqmOyRrl2tXAdMul88-nx9fsew3zDzf-6izvBVSgmY=6mILlAqZ8gMoMkJkP5zwdOs4r9OfPRq7-wFDwMkJr5CN9DfvGKDOnqx_fpLnxuBYB_EGQtMuNltyGR27fyz1TqkBa7z7ELbv7VhLRwVa3wJKP-TiXtBZRHBnvo5mfIlRxzq0=c=Gj6u80l3m8z-kPsYBmHkhkBeOsgLimr4S9ho0DFq3K=iKqcU-=rdYHnHj7ketQx-OyhVVjhLce-_JP=mkoySFE7L3AIiOj24r_czhYcpYV6CSMlUj5hIPrOclhLrZ=PzyBo1UT7K-PrxrauzpwuKwX7D4G84T-5ETKtAEmULtXEB=F2c30xXTgHIqqeHTrRl8mrbXR=7UgJkOeFUJ78kCvT32gOaLQrsfLvJjrk5YxE=paetqjZFq-vs4-ZOJBB-k9bZEX-bD2BwdUyyhEQzFDMzVgSUFDal3Dya3Ipa2zbhdQjHjGnhHIYM3A4Vm_czlTbzLLv6NPYcYF9ofn6smoPUoNQPYIIHDi7qSBmAEKHd1=nlH1Xeb1u4JZLp7P4YJMeTuw3E140bQuaR6FFxlib6qihoLtoVUmyHkjySOvFxQmbU13R0Iewg274dCDkHY=EXziyaKxLj8=PvJ23ZFckvck0-7XlgLRZzetKfo6uFFaaoICPfeHM08CXwjUzdh-pOUoyzmsaZw-wYztFCNuEmXRYqK14ZmjR-5heIMuzMU68JBetprsur3HOL3f5o0Yx=zyovE69vYH43kJm-ptX8_APlknlkAftDOF2tikn8OndHRzzXcn_xJ3L0vGr_hgGhHI8PjavIu5SlF5xqteSml-hxPtx_C25ORDepUtJJrkuEgyJ1FkCALHjJ_-EMlQcjREsusBQCvtzLhKcVtxEFH_P8OpYotnGUnwAjmo=pjS3gFAZHdSeykxxtbg0pdgUKwZUIwSHpSe-flEXJVe7hOEmDDLA8QZR8eOGMQPBE1CNAtlBRN2RM8B5B1ztU2mCvD1gpMUvj=3xCynQMTIVy9apHEpaV8cfSo05C=Bc_G4bbpbFnnith0ekk44=xPmXNkn9IXEjM9AVmTQsH3rdINDrBZ6Nes59Xv0Xn4kikxaozQZUbE-3s_3sR50vIpniRuRPaDU9IfCaFcUK26oGEcXGqAOwJ24n4iZx11oUp=kunuFeIDChSJveiXeZr0_jmCZ=FHX1UHX-fXIK-4VMP-eznJ6z=g=C8RLQGbdEfzbrtZswk8AZO_EHnrSagVCJy5H=JJ-q-lOq2TpDAZ29wXJdldlqnz8XZmJAer2qIaMPOSNVQAeXufN1GR0A=IDysg7oZRJjJV_GzPYQ6e9YqeZQFmVnkLKNwbPkhiTxSK4u13aLRzHDbD8iG=wlOhAP1IyBMngFMYkdg-DHL3KOpyaEf3LDOE3o5GGImitLPYZXUrJZ6pLQpFNOtuROKSiKYm2ZfTLYuz5eMu8ALDI7fZ_N66teGo3lN=B3gl9UH8=_Fzv_KFj4IN5euTQpqRM2VzcNRf4e_HUF5TRSbi5NTHrn2NgpNU87Y9FaEneVSs91q3VRFsA7Beu_9S0NC2UFxOiXftklLrHErCN8UqedeGhckwgg0BpFPup5KxdhUnkUvyHJdshS72-8Z2aoYO-RSH-c7kpJ=BDgmaZONVfVQci9NUu5ePcq6j4F6Ui9uhCTFXM6wG7VJjp=1lNIDFoXtcFPshbhLcrFDYi=ErsV=8JDZU5T_dgUoa6wSkkO_-SttEehsTi4zuo3B-JE9FdnYL-F7dO8wh7_aiZMo5OLLSngPz6B7OD_sJuz=rTiLnb6h4PY5jZphJnRdHtw1IC=GZtYSXpuiEyat5sAhN8PxV6NxRjQ1OpPJQA27k2LOyGlSjPUPiXxJtjwOXOu0xzNlIdJl_4uSXezAXv00uEJNe0DDJg7QUIucGq57jSbX0yh4JiCtl_IEx3m_FCmCncfzbAYgvKPLNgvDblhOH-ahkgFEJ5cF0OafLMMMrBBTCLq8c5dTYeqD_5H7mi2rsTUXOainJuZiqcb6F1H=uRUZ2eCs4wFsk-=1X16e5EAsaU30uUT5P3bQcHJOO3f4DV8lfHX=y-o5_E9uGZNJ0OpGrSHoOtqg26GEqOG=yMjwq9oUIcx7BZP-9r8XHQBOmDOOMK515MkUkld-MYn_MUQEcghSD4zL_E8zcCXTksv5_UV8rqqBveBicN3TQ7IxfQsCguvONFI2CF=-C1Atd2zxrVgY_-6mXGDD1Lime0iPVgXJtGuINvDHQ3k2Ln7LAm2bVMLQLPCQ2fAxF-_XkwyVHhsMXR00pGvUawS6GNDQjprpcsHL9dsRbl_bUTB5wKe2tetFREfFsBkBvpvgFq2YJYLFHluDOTv7VoEe2YZAkSAQhXCkUpECj8_8g3Iv-nr2TaQBvgVx_eETgZHvq9gFAkT0Y2no0xDQ71lYH88uIo5gmMi-naT9-L5BcG50qnMDxg37VqweqVRJV0IE_AX36TF_uZ2u6AzJ-xL0T47jwllxQP5y5tamxRGufEMBEU-eHBdalnDaUcGJM-PoYsPJOKoBGPh8lTUTfIV_E-3ZERdjY_Jtmmw2NhPOASkt1nRweI0ffc=BbUYSj7URj=2qobDeu2Na2KaJaaHjk=izBDsclB8HFQsyDSe5OpjFqmH1dLloE-adEsQ0kAcrv2eTiYZHU27rPoARQ7XVdKDvsU8IuM_67pOKEe2K2A3HsIlwaDAYCav-QtcedYDAyBum6SZDC_EJ6ZgfKjSQcZgTIxCwK0SYdZ97U6MTxsfKEtFfnAf-wGTY2j=okaog_ScsMlGvc8S1ls2eodz6BAYdjLL3=B_dH23GlBBM5K-0p-9AnVY0u4tuaGFzl3dNJeYEp=POMN66iosPZVpgwLySGw2JhUdTiOPhjyg-JF2KxMT5f8RUFb6ei2oRjrrJnrguiCFvzTOAMSI_YZrsaYLmAli_jKjfkGzmJ0fC4CDyGEI827SHT7qzILvQvr7Jr9Ia4=QeBh9N2ht1BmcgSsd92Acb7T3MxHBFNaUQghT_EcyQDLzRXpLPN7hPA86joY7-MJ1kqPE6nxtGGlowHnDLitNbN99tLZDNT1Je-c=xFSuAoVFcgAbaPghZu6tUd8OstAuYXz9XDhKTnXziciHJj0Ol7oRR=54ZQA2CBVxv1IUrMd-8E-9YKneF=oGxCp2olejm=JQcH1xs-4t4qKUrQ15utgPbmxmCU_HVH3ufgEpFmTLILtmFjQ_1DutnNG6RF8ROEYu59maLEM3g8lpmJRrU_t4TnOcBSRpyd6JRdx9ESRCcoPJTPzQD=R6k1HgS4mbh_kCn31Ax79QH4G5ADqMMzSCNNX_xmDB6891Jb42_eDUCiiSJ7AfjECCKxnyHUtJX0fH4eTi_wF0cul_Y-80nnvXhkClrkuTuUc2ckrCEwxL2gjOnBXvae8nlNnJyS8vKxPDXB6UvG3UgEq-ihK9h51OmcwFazXKi4QV8hxfGY7qh-BE6aaZkjrg3o7Zy8oLtHIoc_09XBH=A5eH1swmwblE4=AmrKKAygVwyojvjI2ockQXya7aFuDRfkdp3s0yVBCxukTetccnsdNqGmJ3yP=qr5e__BC8KoeSc=wy6ZDeV"
        x_f = "A7lM_aZ-AQAANzhfZt5A322-x_uQC9hfsrsfDjrseCJrYcXHgtM5KhDeNK2yAWDyDnmuct61wH8AAOfvAAAAAA=="
        x_c = "ACA-1aZ-AQAA6N35qCXogi-BoHNhlFYLtqMS4sv3NpB1gw1ILw-2AA0Op78z"
        x_b = "fhp8zc"
        headers = {
            "X-XSRF-TOKEN": self.xsrf_token,
            "X-zuY25QsG-c": x_c,
            "X-zuY25QsG-z": "p",
            "User-Agent": self.user_agent,
            "X-zuY25QsG-b": x_b,
            "X-zuY25QsG-a": x_a,
            "ADP-Device-Fingerprint": self.finger_print,
            "Content-Type": "application/json",
            "X-zuY25QsG-f": x_f,
            "X-zuY25QsG-d": "o_0",
        }
        next_url = (
            "https://online.adp.com/api/sign-in-service/v1/sign-in.account.identify"
        )
        sign_in_account_identify = self.post(
            next_url, data=json.dumps(data), headers=headers
        )
        if sign_in_account_identify.status_code != 200:
            return False
        # signed in successfully
        return True

    def handle_signin_password(self):
        data = {
            "response": {
                "type": "PASSWORD_VERIFICATION_RESPONSE",
                "password": self.password,
                "locale": "en_US",
            },
            "session": self.adp_session,
        }
        headers = {
            "X-XSRF-TOKEN": self.xsrf_token,
            "X-zuY25QsG-z": "p",
            "User-Agent": self.user_agent,
            "ADP-Device-Fingerprint": self.finger_print,
            "Content-Type": "application/json",
            "X-zuY25QsG-d": "o_0",
        }
        next_url = "https://online.adp.com/api/sign-in-service/v1/sign-in.challenge.respond"
        sign_in_challenge_res = self.post(next_url, data=json.dumps(data), headers=headers)
        return sign_in_challenge_res.json()

    def is_successful_log_in(self, data):
        if data.get('status') == 500:
            # 'An internal server error occurred'
            # likely due to cookies being mismatched with generated xsrf token
            raise Exception(f"Submitting password failed with 500. Check that cookies are valid")
        if data.get('status', 200) != 200:
            raise Exception("sign in response must be 200")
        # confirm that user is signed in correctly
        result_type = data["result"]["type"]
        if result_type != "SIGNED_IN":
            return False
        # signed in successfully
        return True

    def sign_out(self):
        # TODO: maybe create a sign out
        pass

    def requests_login(self):
        self.handle_login_cookies()
        self.handle_signin_start()
        self.handle_signin_username()
        logged_in_page = self.handle_signin_password()
        self.is_successful_log_in(logged_in_page)

    def get_pay_statements(self, num_of_paydates: int):
        statements_page = self.get(
            "https://my.adp.com/myadp_prefix/v1_0/O/A/payStatements",
            params={
                "adjustments": "yes",
                "numberoflastpaydates": str(num_of_paydates),
            },
        )
        return statements_page.json()

    def get_pay_statement_dates(self, num_of_paydates: int):
        """
        :return:
            return pay dates for n number of statements
        """
        statements = self.get_pay_statements(num_of_paydates=num_of_paydates)
        return [statement["payDate"] for statement in statements["payStatements"]]

    def chrome_dynamic_typing(self, driver, chars):
        """
        Simulate natural typing
        """
        action = ActionChains(driver)
        for char in chars:
            action.send_keys(Keys.COMMAND + char).perform()
            # pause randomly for between 0 - 1 seconds to simulate natural typing
            time.sleep(random.random())

    def chrome_driver_login(self, natural_typing=True):
        driver = webdriver.Chrome("/Users/olehdubno/Documents/chromedriver")
        login_url = "https://my.adp.com/"
        driver.get(login_url)

        time.sleep(4)  # TODO (there's a smarter way to wait for an element)
        # ADP is affective at identifying when selenium is used
        # I don't think it's impossible but at this moment this is taking too much of my time
        if natural_typing:
            self.chrome_dynamic_typing(driver, self.username)
            self.chrome_dynamic_typing(driver, Keys.ENTER)
        else:
            driver.find_element_by_xpath(
                '//input[@id="login-form_username"]'
            ).send_keys(self.username)
            e = driver.find_element_by_xpath('//button[@id="verifUseridBtn"]')
            e.send_keys(Keys.ENTER)
        # both dynamic and element selection cases fail with
        # Application Error. Please try again Later[]

        # TODO (maybe use driver to load desired cookied into session
        for cookie in driver.get_cookies():
            self.session.cookies.set(cookie["name"], cookie["value"])


if __name__ == "__main__":
    pass
    # crawl = ADPCrawler("test", "test")
    # crawl.requests_login()
    # crawl.get_pay_statement_dates(160)
