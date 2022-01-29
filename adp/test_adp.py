from adp.adp import ADPCrawler


class TestADPCrawler(ADPCrawler):

    def handle_signin_password(self):
        return {
            "result": {
                "accessToken": "",
                "redirectUrl": "https://my.adp.com/static/redbox/",
                "user": {"givenName": "TEST"},
                "type": "SIGNED_IN",
            }
        }

    def get_pay_statements(self, num_of_paydates: int):
        return {
            "payStatements": [
                {
                    "payDate": "2022-01-14",
                    "netPayAmount": {"amountValue": 1234.12, "currencyCode": "USD"},
                    "grossPayAmount": {"amountValue": 4321.21, "currencyCode": "USD"},
                    "totalHours": 86.67,
                    "payDetailUri": {
                        "href": "/v1_0/O/A/payStatement/0301167422023676100304001520174"
                    },
                    "statementImageUri": {
                        "href": "/l2/v1_0/O/A/payStatement/0301167422023676100304001520174/images/DQ7ooo005044200000r034A4D99CD3621.pdf"
                    },
                    "payAdjustmentIndicator": False,
                },
                {
                    "payDate": "2021-12-30",
                    "netPayAmount": {"amountValue": 1234.12, "currencyCode": "USD"},
                    "grossPayAmount": {"amountValue": 4321.21, "currencyCode": "USD"},
                    "totalHours": 86.67,
                    "payDetailUri": {
                        "href": "/v1_0/O/A/payStatement/0301167421521460100304001770463"
                    },
                    "statementImageUri": {
                        "href": "/l2/v1_0/O/A/payStatement/0301167421521460100304001770463/images/DQ7ooo000930250000r03EECB21BC1621.pdf"
                    },
                    "payAdjustmentIndicator": False,
                },
                {
                    "payDate": "2021-12-15",
                    "netPayAmount": {"amountValue": 1234.12, "currencyCode": "USD"},
                    "grossPayAmount": {"amountValue": 4321.21, "currencyCode": "USD"},
                    "totalHours": 86.67,
                    "payDetailUri": {
                        "href": "/v1_0/O/A/payStatement/0301167421508004100304001292260"
                    },
                    "statementImageUri": {
                        "href": "/l2/v1_0/O/A/payStatement/0301167421508004100304001292260/images/DQ7ooo004930050000r030DAED2AC1621.pdf"
                    },
                    "payAdjustmentIndicator": False,
                },
            ],
            "retirementPlanIndicator": False,
        }


def test_adp_get_pay_statement_dates():
    crawl = TestADPCrawler("test", "test")
    crawl.requests_login()
    result_dates = crawl.get_pay_statement_dates(2)
    assert result_dates == ["2022-01-14", "2021-12-30", "2021-12-15"]
