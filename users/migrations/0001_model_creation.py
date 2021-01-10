# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
import re2o.mixins
import re2o.field_permissions
import users.models


class Migration(migrations.Migration):
    dependencies = [('auth', '0008_alter_user_username_max_length')]
    initial = True
    # We replace everything.
    replaces = [
        ("users", "0001_initial"),
        ("users", "0002_auto_20160630_2301"),
        ("users", "0003_listrights_rights"),
        ("users", "0004_auto_20160701_2312"),
        ("users", "0005_auto_20160702_0006"),
        ("users", "0006_ban"),
        ("users", "0007_auto_20160702_2322"),
        ("users", "0008_user_registered"),
        ("users", "0009_user_room"),
        ("users", "0010_auto_20160703_1226"),
        ("users", "0011_auto_20160703_1227"),
        ("users", "0012_auto_20160703_1230"),
        ("users", "0013_auto_20160704_1547"),
        ("users", "0014_auto_20160704_1548"),
        ("users", "0015_whitelist"),
        ("users", "0016_auto_20160706_1220"),
        ("users", "0017_auto_20160707_0105"),
        ("users", "0018_auto_20160707_0115"),
        ("users", "0019_auto_20160708_1633"),
        ("users", "0020_request"),
        ("users", "0021_ldapuser"),
        ("users", "0022_ldapuser_sambasid"),
        ("users", "0023_auto_20160724_1908"),
        ("users", "0024_remove_ldapuser_mac_list"),
        ("users", "0025_listshell"),
        ("users", "0026_user_shell"),
        ("users", "0027_auto_20160726_0216"),
        ("users", "0028_auto_20160726_0227"),
        ("users", "0029_auto_20160726_0229"),
        ("users", "0030_auto_20160726_0357"),
        ("users", "0031_auto_20160726_0359"),
        ("users", "0032_auto_20160727_2122"),
        ("users", "0033_remove_ldapuser_loginshell"),
        ("users", "0034_auto_20161018_0037"),
        ("users", "0035_auto_20161018_0046"),
        ("users", "0036_auto_20161022_2146"),
        ("users", "0037_auto_20161028_1906"),
        ("users", "0038_auto_20161031_0258"),
        ("users", "0039_auto_20161119_0033"),
        ("users", "0040_auto_20161119_1709"),
        ("users", "0041_listright_details"),
        ("users", "0042_auto_20161126_2028"),
        ("users", "0043_auto_20161224_1156"),
        ("users", "0043_ban_state"),
        ("users", "0044_user_ssh_public_key"),
        ("users", "0045_merge"),
        ("users", "0046_auto_20170617_1433"),
        ("users", "0047_auto_20170618_0156"),
        ("users", "0048_auto_20170618_0210"),
        ("users", "0049_auto_20170618_1424"),
        ("users", "0050_serviceuser_comment"),
        ("users", "0051_user_telephone"),
        ("users", "0052_ldapuser_shadowexpire"),
        ("users", "0053_auto_20170626_2105"),
        ("users", "0054_auto_20170626_2219"),
        ("users", "0055_auto_20171003_0556"),
        ("users", "0056_auto_20171015_2033"),
        ("users", "0057_auto_20171023_0301"),
        ("users", "0058_auto_20171025_0154"),
        ("users", "0059_auto_20171025_1854"),
        ("users", "0060_auto_20171120_0317"),
        ("users", "0061_auto_20171230_2033"),
        ("users", "0062_auto_20171231_0056"),
        ("users", "0063_auto_20171231_0140"),
        ("users", "0064_auto_20171231_0150"),
        ("users", "0065_auto_20171231_2053"),
        ("users", "0066_grouppermissions"),
        ("users", "0067_serveurpermission"),
        ("users", "0068_auto_20180107_2245"),
        ("users", "0069_club_mailing"),
        ("users", "0070_auto_20180324_1906"),
        ("users", "0071_auto_20180415_1252"),
        ("users", "0072_auto_20180426_2021"),
        ("users", "0073_auto_20180629_1614"),
        ("users", "0074_auto_20180810_2104"),
        ("users", "0074_auto_20180814_1059"),
        ("users", "0075_merge_20180815_2202"),
        ("users", "0076_auto_20180818_1321"),
        ("users", "0077_auto_20180824_1750"),
        ("users", "0078_auto_20181011_1405"),
        ("users", "0079_auto_20181228_2039"),
        ("users", "0080_auto_20190108_1726"),
        ("users", "0081_auto_20190317_0302"),
        ("users", "0082_auto_20190908_1338"),
        ("users", "0083_user_shortcuts_enabled"),
        ("users", "0084_auto_20191120_0159"),
        ("users", "0085_user_email_state"),
        ("users", "0086_user_email_change_date"),
        ("users", "0087_request_email"),
        ("users", "0088_auto_20200417_2312"),
        ("users", "0089_auto_20200418_0112"),
        ("users", "0090_auto_20200421_1825"),
        ("users", "0091_auto_20200423_1256"),
        ("users", "0092_auto_20200502_0057"),
        ("users", "0093_user_profile_image"),
        ("users", "0094_remove_user_profile_image"),
        ("users", "0095_user_theme"),
        ("cotisations", "0001_initial"),
        ("cotisations", "0002_remove_facture_article"),
        ("cotisations", "0003_auto_20160702_1448"),
        ("cotisations", "0004_auto_20160702_1528"),
        ("cotisations", "0005_auto_20160702_1532"),
        ("cotisations", "0006_auto_20160702_1534"),
        ("cotisations", "0007_auto_20160702_1543"),
        ("cotisations", "0008_auto_20160702_1614"),
        ("cotisations", "0009_remove_cotisation_user"),
        ("cotisations", "0010_auto_20160702_1840"),
        ("cotisations", "0011_auto_20160702_1911"),
        ("cotisations", "0012_auto_20160704_0118"),
        ("cotisations", "0013_auto_20160711_2240"),
        ("cotisations", "0014_auto_20160712_0245"),
        ("cotisations", "0015_auto_20160714_2142"),
        ("cotisations", "0016_auto_20160715_0110"),
        ("cotisations", "0017_auto_20170718_2329"),
        ("cotisations", "0018_paiement_type_paiement"),
        ("cotisations", "0019_auto_20170819_0055"),
        ("cotisations", "0020_auto_20170819_0057"),
        ("cotisations", "0021_auto_20170819_0104"),
        ("cotisations", "0022_auto_20170824_0128"),
        ("cotisations", "0023_auto_20170902_1303"),
        ("cotisations", "0024_auto_20171015_2033"),
        ("cotisations", "0025_article_type_user"),
        ("cotisations", "0026_auto_20171028_0126"),
        ("cotisations", "0027_auto_20171029_1156"),
        ("cotisations", "0028_auto_20171231_0007"),
        ("cotisations", "0029_auto_20180414_2056"),
        ("cotisations", "0030_custom_payment"),
        ("cotisations", "0031_comnpaypayment_production"),
        ("cotisations", "0032_custom_invoice"),
        ("cotisations", "0033_auto_20180818_1319"),
        ("cotisations", "0034_auto_20180831_1532"),
        ("cotisations", "0035_notepayment"),
        ("cotisations", "0036_custominvoice_remark"),
        ("cotisations", "0037_costestimate"),
        ("cotisations", "0038_auto_20181231_1657"),
        ("cotisations", "0039_freepayment"),
        ("cotisations", "0040_auto_20191002_2335"),
        ("cotisations", "0041_auto_20191103_2131"),
        ("cotisations", "0042_auto_20191120_0159"),
        ("cotisations", "0043_separation_membership_connection_p1"),
        ("cotisations", "0044_separation_membership_connection_p2"),
        ("cotisations", "0045_separation_membership_connection_p3"),
        ("cotisations", "0046_article_need_membership"),
        ("cotisations", "0047_article_need_membership_init"),
        ("cotisations", "0048_auto_20201017_0018"),
        ("cotisations", "0049_auto_20201102_2305"),
        ("cotisations", "0050_auto_20201102_2342"),
        ("cotisations", "0051_auto_20201228_1636"),
        ("machines", "0001_initial"),
        ("machines", "0002_auto_20160703_1444"),
        ("machines", "0003_auto_20160703_1450"),
        ("machines", "0004_auto_20160703_1451"),
        ("machines", "0005_auto_20160703_1523"),
        ("machines", "0006_auto_20160703_1813"),
        ("machines", "0007_auto_20160703_1816"),
        ("machines", "0008_remove_interface_ipv6"),
        ("machines", "0009_auto_20160703_2358"),
        ("machines", "0010_auto_20160704_0104"),
        ("machines", "0011_auto_20160704_0105"),
        ("machines", "0012_auto_20160704_0118"),
        ("machines", "0013_auto_20160705_1014"),
        ("machines", "0014_auto_20160706_1220"),
        ("machines", "0015_auto_20160707_0105"),
        ("machines", "0016_auto_20160708_1633"),
        ("machines", "0017_auto_20160708_1645"),
        ("machines", "0018_auto_20160708_1813"),
        ("machines", "0019_auto_20160718_1141"),
        ("machines", "0020_auto_20160718_1849"),
        ("machines", "0021_auto_20161006_1943"),
        ("machines", "0022_auto_20161011_1829"),
        ("machines", "0023_iplist_ip_type"),
        ("machines", "0024_machinetype_need_infra"),
        ("machines", "0025_auto_20161023_0038"),
        ("machines", "0026_auto_20161026_1348"),
        ("machines", "0027_alias"),
        ("machines", "0028_iptype_domaine_ip"),
        ("machines", "0029_iptype_domaine_range"),
        ("machines", "0030_auto_20161118_1730"),
        ("machines", "0031_auto_20161119_1709"),
        ("machines", "0032_auto_20161119_1850"),
        ("machines", "0033_extension_need_infra"),
        ("machines", "0034_iplist_need_infra"),
        ("machines", "0035_auto_20161224_1201"),
        ("machines", "0036_auto_20161224_1204"),
        ("machines", "0037_domain_cname"),
        ("machines", "0038_auto_20161224_1721"),
        ("machines", "0039_auto_20161224_1732"),
        ("machines", "0040_remove_interface_dns"),
        ("machines", "0041_remove_ns_interface"),
        ("machines", "0042_ns_ns"),
        ("machines", "0043_auto_20170721_0350"),
        ("machines", "0044_auto_20170808_0233"),
        ("machines", "0045_auto_20170808_0348"),
        ("machines", "0046_auto_20170808_1423"),
        ("machines", "0047_auto_20170809_0606"),
        ("machines", "0048_auto_20170823_2315"),
        ("machines", "0049_vlan"),
        ("machines", "0050_auto_20170826_0022"),
        ("machines", "0051_iptype_vlan"),
        ("machines", "0052_auto_20170828_2322"),
        ("machines", "0053_text"),
        ("machines", "0054_text_zone"),
        ("machines", "0055_nas"),
        ("machines", "0056_nas_port_access_mode"),
        ("machines", "0057_nas_autocapture_mac"),
        ("machines", "0058_auto_20171002_0350"),
        ("machines", "0059_iptype_prefix_v6"),
        ("machines", "0060_iptype_ouverture_ports"),
        ("machines", "0061_auto_20171015_2033"),
        ("machines", "0062_extension_origin_v6"),
        ("machines", "0063_auto_20171020_0040"),
        ("machines", "0064_auto_20171115_0253"),
        ("machines", "0065_auto_20171115_1514"),
        ("machines", "0066_srv"),
        ("machines", "0067_auto_20171116_0152"),
        ("machines", "0068_auto_20171116_0252"),
        ("machines", "0069_auto_20171116_0822"),
        ("machines", "0070_auto_20171231_1947"),
        ("machines", "0071_auto_20171231_2100"),
        ("machines", "0072_auto_20180108_1822"),
        ("machines", "0073_auto_20180128_2203"),
        ("machines", "0074_auto_20180129_0352"),
        ("machines", "0075_auto_20180130_0052"),
        ("machines", "0076_auto_20180130_1623"),
        ("machines", "0077_auto_20180409_2243"),
        ("machines", "0078_auto_20180415_1252"),
        ("machines", "0079_auto_20180416_0107"),
        ("machines", "0080_auto_20180502_2334"),
        ("machines", "0081_auto_20180521_1413"),
        ("machines", "0082_auto_20180525_2209"),
        ("machines", "0083_remove_duplicate_rights"),
        ("machines", "0084_dname"),
        ("machines", "0085_sshfingerprint"),
        ("machines", "0086_role"),
        ("machines", "0087_dnssec"),
        ("machines", "0088_iptype_prefix_v6_length"),
        ("machines", "0089_auto_20180805_1148"),
        ("machines", "0090_auto_20180805_1459"),
        ("machines", "0091_auto_20180806_2310"),
        ("machines", "0092_auto_20180807_0926"),
        ("machines", "0093_auto_20180807_1115"),
        ("machines", "0094_auto_20180815_1918"),
        ("machines", "0095_auto_20180919_2225"),
        ("machines", "0096_auto_20181013_1417"),
        ("machines", "0097_extension_dnssec"),
        ("machines", "0098_auto_20190102_1745"),
        ("machines", "0099_role_recursive_dns"),
        ("machines", "0100_auto_20190102_1753"),
        ("machines", "0101_auto_20190108_1623"),
        ("machines", "0102_auto_20190303_1611"),
        ("machines", "0103_auto_20191002_2222"),
        ("machines", "0104_auto_20191002_2231"),
        ("machines", "0105_dname_ttl"),
        ("machines", "0106_auto_20191120_0159"),
        ("machines", "0107_fix_lowercase_domain"),
        ("machines", "0108_ipv6list_active"),
        ("preferences", "0001_initial"),
        ("preferences", "0002_auto_20170625_1923"),
        ("preferences", "0003_optionaluser_solde_negatif"),
        ("preferences", "0004_assooption_services"),
        ("preferences", "0005_auto_20170824_0139"),
        ("preferences", "0006_auto_20170824_0143"),
        ("preferences", "0007_auto_20170824_2056"),
        ("preferences", "0008_auto_20170824_2122"),
        ("preferences", "0009_assooption_utilisateur_asso"),
        ("preferences", "0010_auto_20170825_0459"),
        ("preferences", "0011_auto_20170825_2307"),
        ("preferences", "0012_generaloption_req_expire_hrs"),
        ("preferences", "0013_generaloption_site_name"),
        ("preferences", "0014_generaloption_email_from"),
        ("preferences", "0015_optionaltopologie_radius_general_policy"),
        ("preferences", "0016_auto_20170902_1520"),
        ("preferences", "0017_mailmessageoption"),
        ("preferences", "0018_optionaltopologie_mac_autocapture"),
        ("preferences", "0019_remove_optionaltopologie_mac_autocapture"),
        ("preferences", "0020_optionalmachine_ipv6"),
        ("preferences", "0021_auto_20171015_1741"),
        ("preferences", "0022_auto_20171015_1758"),
        ("preferences", "0023_auto_20171015_2033"),
        ("preferences", "0024_optionaluser_all_can_create"),
        ("preferences", "0025_auto_20171231_2142"),
        ("preferences", "0025_generaloption_general_message"),
        ("preferences", "0026_auto_20171216_0401"),
        ("preferences", "0027_merge_20180106_2019"),
        ("preferences", "0028_assooption_description"),
        ("preferences", "0028_auto_20180111_1129"),
        ("preferences", "0028_auto_20180128_2203"),
        ("preferences", "0029_auto_20180111_1134"),
        ("preferences", "0029_auto_20180318_0213"),
        ("preferences", "0029_auto_20180318_1005"),
        ("preferences", "0030_auto_20180111_2346"),
        ("preferences", "0030_merge_20180320_1419"),
        ("preferences", "0031_auto_20180323_0218"),
        ("preferences", "0031_optionaluser_self_adhesion"),
        ("preferences", "0032_optionaluser_min_online_payment"),
        ("preferences", "0032_optionaluser_shell_default"),
        ("preferences", "0033_accueiloption"),
        ("preferences", "0033_generaloption_gtu_sum_up"),
        ("preferences", "0034_auto_20180114_2025"),
        ("preferences", "0034_auto_20180416_1120"),
        ("preferences", "0035_auto_20180114_2132"),
        ("preferences", "0035_optionaluser_allow_self_subscription"),
        ("preferences", "0036_auto_20180114_2141"),
        ("preferences", "0037_auto_20180114_2156"),
        ("preferences", "0038_auto_20180114_2209"),
        ("preferences", "0039_auto_20180115_0003"),
        ("preferences", "0040_auto_20180129_1745"),
        ("preferences", "0041_merge_20180130_0052"),
        ("preferences", "0042_auto_20180222_1743"),
        ("preferences", "0043_optionalmachine_create_machine"),
        ("preferences", "0044_remove_payment_pass"),
        ("preferences", "0045_remove_unused_payment_fields"),
        ("preferences", "0046_optionaluser_mail_extension"),
        ("preferences", "0047_mailcontact"),
        ("preferences", "0048_auto_20180811_1515"),
        ("preferences", "0049_optionaluser_self_change_shell"),
        ("preferences", "0050_auto_20180818_1329"),
        ("preferences", "0051_auto_20180919_2225"),
        ("preferences", "0052_optionaluser_delete_notyetactive"),
        ("preferences", "0053_optionaluser_self_change_room"),
        ("preferences", "0055_generaloption_main_site_url"),
        ("preferences", "0056_1_radiusoption"),
        ("preferences", "0056_2_radiusoption"),
        ("preferences", "0056_3_radiusoption"),
        ("preferences", "0056_4_radiusoption"),
        ("preferences", "0057_optionaluser_all_users_active"),
        ("preferences", "0058_auto_20190108_1650"),
        ("preferences", "0059_auto_20190120_1739"),
        ("preferences", "0060_auto_20190712_1821"),
        ("preferences", "0061_optionaluser_allow_archived_connexion"),
        ("preferences", "0062_auto_20190910_1909"),
        ("preferences", "0063_mandate"),
        ("preferences", "0064_auto_20191008_1335"),
        ("preferences", "0065_auto_20191010_1227"),
        ("preferences", "0066_optionalmachine_default_dns_ttl"),
        ("preferences", "0067_auto_20191120_0159"),
        ("preferences", "0068_optionaluser_allow_set_password_during_user_creation"),
        ("preferences", "0069_optionaluser_disable_emailnotyetconfirmed"),
        ("preferences", "0070_auto_20200419_0225"),
        ("preferences", "0071_optionaluser_self_change_pseudo"),
        ("topologie", "0001_initial"),
        ("topologie", "0002_auto_20160703_1118"),
        ("topologie", "0003_room"),
        ("topologie", "0004_auto_20160703_1122"),
        ("topologie", "0005_auto_20160703_1123"),
        ("topologie", "0006_auto_20160703_1129"),
        ("topologie", "0007_auto_20160703_1148"),
        ("topologie", "0008_port_room"),
        ("topologie", "0009_auto_20160703_1200"),
        ("topologie", "0010_auto_20160704_2148"),
        ("topologie", "0011_auto_20160704_2153"),
        ("topologie", "0012_port_machine_interface"),
        ("topologie", "0013_port_related"),
        ("topologie", "0014_auto_20160706_1238"),
        ("topologie", "0015_auto_20160706_1452"),
        ("topologie", "0016_auto_20160706_1531"),
        ("topologie", "0017_auto_20160718_1141"),
        ("topologie", "0018_room_details"),
        ("topologie", "0019_auto_20161026_1348"),
        ("topologie", "0020_auto_20161119_0033"),
        ("topologie", "0021_port_radius"),
        ("topologie", "0022_auto_20161211_1622"),
        ("topologie", "0023_auto_20170817_1654"),
        ("topologie", "0023_auto_20170826_1530"),
        ("topologie", "0024_auto_20170818_1021"),
        ("topologie", "0024_auto_20170826_1800"),
        ("topologie", "0025_merge_20170902_1242"),
        ("topologie", "0026_auto_20170902_1245"),
        ("topologie", "0027_auto_20170905_1442"),
        ("topologie", "0028_auto_20170913_1503"),
        ("topologie", "0029_auto_20171002_0334"),
        ("topologie", "0030_auto_20171004_0235"),
        ("topologie", "0031_auto_20171015_2033"),
        ("topologie", "0032_auto_20171026_0338"),
        ("topologie", "0033_auto_20171231_1743"),
        ("topologie", "0034_borne"),
        ("topologie", "0035_auto_20180324_0023"),
        ("topologie", "0036_transferborne"),
        ("topologie", "0037_auto_20180325_0127"),
        ("topologie", "0038_transfersw"),
        ("topologie", "0039_port_new_switch"),
        ("topologie", "0040_transferports"),
        ("topologie", "0041_transferportsw"),
        ("topologie", "0042_transferswitch"),
        ("topologie", "0043_renamenewswitch"),
        ("topologie", "0044_auto_20180326_0002"),
        ("topologie", "0045_auto_20180326_0123"),
        ("topologie", "0046_auto_20180326_0129"),
        ("topologie", "0047_ap_machine"),
        ("topologie", "0048_ap_machine"),
        ("topologie", "0049_switchs_machine"),
        ("topologie", "0050_port_new_switch"),
        ("topologie", "0051_switchs_machine"),
        ("topologie", "0052_transferports"),
        ("topologie", "0053_finalsw"),
        ("topologie", "0054_auto_20180326_1742"),
        ("topologie", "0055_auto_20180329_0431"),
        ("topologie", "0056_building_switchbay"),
        ("topologie", "0057_auto_20180408_0316"),
        ("topologie", "0058_remove_switch_location"),
        ("topologie", "0059_auto_20180415_2249"),
        ("topologie", "0060_server"),
        ("topologie", "0061_portprofile"),
        ("topologie", "0062_auto_20180815_1918"),
        ("topologie", "0063_auto_20180919_2225"),
        ("topologie", "0064_switch_automatic_provision"),
        ("topologie", "0065_auto_20180927_1836"),
        ("topologie", "0066_modelswitch_commercial_name"),
        ("topologie", "0067_auto_20181230_1819"),
        ("topologie", "0068_auto_20190102_1758"),
        ("topologie", "0069_auto_20190108_1439"),
        ("topologie", "0070_auto_20190218_1743"),
        ("topologie", "0071_auto_20190218_1936"),
        ("topologie", "0072_auto_20190720_2318"),
        ("topologie", "0073_auto_20191120_0159"),
        ("topologie", "0074_auto_20200419_1640"),
    ]
    operations = [
        migrations.CreateModel(
            name="User",
            bases=(
                re2o.mixins.RevMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
                django.contrib.auth.models.AbstractBaseUser,
                django.contrib.auth.models.PermissionsMixin,
                re2o.mixins.AclMixin,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("surname", models.CharField(max_length=255)),
                (
                    "pseudo",
                    models.CharField(
                        max_length=32,
                        unique=True,
                        help_text="Must only contain letters, numerals or dashes.",
                        validators=[users.models.linux_user_validator],
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        default="",
                        help_text="External email address allowing us to contact you.",
                    ),
                ),
                (
                    "local_email_redirect",
                    models.BooleanField(
                        default=False,
                        help_text="Enable redirection of the local email messages to the main email address.",
                    ),
                ),
                (
                    "local_email_enabled",
                    models.BooleanField(
                        default=False, help_text="Enable the local email account."
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        help_text="Comment, school year.", max_length=255, blank=True
                    ),
                ),
                ("pwd_ntlm", models.CharField(max_length=255)),
                (
                    "state",
                    models.IntegerField(
                        choices=(
                            (0, "Active"),
                            (1, "Disabled"),
                            (2, "Archived"),
                            (3, "Not yet active"),
                            (4, "Fully archived"),
                        ),
                        default=3,
                        help_text="Account state.",
                    ),
                ),
                (
                    "email_state",
                    models.IntegerField(
                        choices=(
                            (0, "Confirmed"),
                            (1, "Not confirmed"),
                            (2, "Waiting for email confirmation"),
                        ),
                        default=2,
                    ),
                ),
                ("registered", models.DateTimeField(auto_now_add=True)),
                ("telephone", models.CharField(max_length=15, blank=True, null=True)),
                (
                    "uid_number",
                    models.PositiveIntegerField(
                        default=users.models.get_fresh_user_uid, unique=True
                    ),
                ),
                (
                    "legacy_uid",
                    models.PositiveIntegerField(
                        unique=True,
                        blank=True,
                        null=True,
                        help_text="Optionnal legacy uid, for import and transition purpose",
                    ),
                ),
                (
                    "shortcuts_enabled",
                    models.BooleanField(
                        verbose_name="enable shortcuts on Re2o website", default=True
                    ),
                ),
                ("email_change_date", models.DateTimeField(auto_now_add=True)),
                ("theme", models.CharField(max_length=255, default="default.css")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128, verbose_name="password"
                    ),
                ),
                ("groups", models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ("user_permissions", models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'))
            ],
            options={
                "permissions": (
                    ("change_user_password", "Can change the password of a user"),
                    ("change_user_state", "Can edit the state of a user"),
                    ("change_user_force", "Can force the move"),
                    ("change_user_shell", "Can edit the shell of a user"),
                    ("change_user_pseudo", "Can edit the pseudo of a user"),
                    (
                        "change_user_groups",
                        "Can edit the groups of rights of a user (critical permission)",
                    ),
                    (
                        "change_all_users",
                        "Can edit all users, including those with rights",
                    ),
                    ("view_user", "Can view a user object"),
                ),
                "verbose_name": "user (member or club)",
                "verbose_name_plural": "users (members or clubs)",
            },
        ),
        migrations.CreateModel(
            name="Adherent",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "gpg_fingerprint",
                    models.CharField(max_length=49, blank=True, null=True),
                ),
            ],
            options={"verbose_name": "member", "verbose_name_plural": "members"},
        ),
        migrations.CreateModel(
            name="Club",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("mailing", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "club", "verbose_name_plural": "clubs"},
        ),
        migrations.CreateModel(
            name="ServiceUser",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                django.contrib.auth.models.AbstractBaseUser,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "pseudo",
                    models.CharField(
                        max_length=32,
                        unique=True,
                        help_text="Must only contain letters, numerals or dashes.",
                        validators=[users.models.linux_user_validator],
                    ),
                ),
                (
                    "access_group",
                    models.CharField(
                        choices=(
                            ("auth", "auth"),
                            ("readonly", "readonly"),
                            ("usermgmt", "usermgmt"),
                        ),
                        default="readonly",
                        max_length=32,
                    ),
                ),
                (
                    "comment",
                    models.CharField(help_text="Comment.", max_length=255, blank=True),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128, verbose_name="password"
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_serviceuser", "Can view a service user object"),
                ),
                "verbose_name": "service user",
                "verbose_name_plural": "service users",
            },
        ),
        migrations.CreateModel(
            name="School",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "permissions": (("view_school", "Can view a school object"),),
                "verbose_name": "school",
                "verbose_name_plural": "schools",
            },
        ),
        migrations.CreateModel(
            name="ListRight",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                django.contrib.auth.models.Group,
            ),
            fields=[
                (
                    "group_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        serialize=False,
                        to="auth.Group",
                    ),
                ),
                (
                    "unix_name",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[a-z]+$",
                                message=(
                                    "UNIX group names can only contain lower case letters."
                                ),
                            )
                        ],
                    ),
                ),
                ("gid", models.PositiveIntegerField(unique=True, null=True)),
                ("critical", models.BooleanField(default=False)),
                (
                    "details",
                    models.CharField(
                        help_text="Description.", max_length=255, blank=True
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_listright", "Can view a group of rights object"),
                ),
                "verbose_name": "group of rights",
                "verbose_name_plural": "groups of rights",
            },
        ),
        migrations.CreateModel(
            name="ListShell",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("shell", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "permissions": (("view_listshell", "Can view a shell object"),),
                "verbose_name": "shell",
                "verbose_name_plural": "shells",
            },
        ),
        migrations.CreateModel(
            name="Ban",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("raison", models.CharField(max_length=255)),
                ("date_start", models.DateTimeField(auto_now_add=True)),
                ("date_end", models.DateTimeField()),
                (
                    "state",
                    models.IntegerField(
                        choices=(
                            (0, "HARD (no access)"),
                            (1, "SOFT (local access only)"),
                            (2, "RESTRICTED (speed limitation)"),
                        ),
                        default=0,
                    ),
                ),
            ],
            options={
                "permissions": (("view_ban", "Can view a ban object"),),
                "verbose_name": "ban",
                "verbose_name_plural": "bans",
            },
        ),
        migrations.CreateModel(
            name="Whitelist",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("raison", models.CharField(max_length=255)),
                ("date_start", models.DateTimeField(auto_now_add=True)),
                ("date_end", models.DateTimeField()),
            ],
            options={
                "permissions": (("view_whitelist", "Can view a whitelist object"),),
                "verbose_name": "whitelist (free of charge access)",
                "verbose_name_plural": "whitelists (free of charge access)",
            },
        ),
        migrations.CreateModel(
            name="Request",
            bases=(models.Model,),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        max_length=2,
                        choices=(("PW", "Password"), ("EM", "Email address")),
                    ),
                ),
                ("token", models.CharField(max_length=32)),
                ("email", models.EmailField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("expires_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="EMailAddress",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "local_part",
                    models.CharField(
                        unique=True,
                        max_length=128,
                        help_text="Local part of the email address.",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_emailaddress", "Can view a local email account object"),
                ),
                "verbose_name": "local email account",
                "verbose_name_plural": "local email accounts",
            },
        ),
    ]
