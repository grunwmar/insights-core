import doctest
import pytest
from insights.core.exceptions import ParseException
from insights.parsers import snmp
from insights.parsers.snmp import TcpIpStats
from insights.parsers.snmp import TcpIpStatsIPV6
from insights.parsers.snmp import SnmpdConf
from insights.tests import context_wrap

PROC_SNMP = """
Ip: Forwarding DefaultTTL InReceives InHdrErrors InAddrErrors ForwDatagrams InUnknownProtos InDiscards InDelivers OutRequests OutDiscards OutNoRoutes ReasmTimeout ReasmReqds ReasmOKs ReasmFails FragOKs FragFails FragCreates
Ip: 2 64 2628 0 2 0 0 0 2624 1618 0 0 0 0 0 10 0 0 0
Icmp: InMsgs InErrors InDestUnreachs InTimeExcds InParmProbs InSrcQuenchs InRedirects InEchos InEchoReps InTimestamps InTimestampReps InAddrMasks InAddrMaskReps OutMsgs OutErrors OutDestUnreachs OutTimeExcds OutParmProbs OutSrcQuenchs OutRedirects OutEchos OutEchoReps OutTimestamps OutTimestampReps OutAddrMasks OutAddrMaskReps
Icmp: 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 2 0 0 0 0 0 0 0 0 0 0
IcmpMsg: InType3 OutType3
IcmpMsg: 34 44
Tcp: RtoAlgorithm RtoMin RtoMax MaxConn ActiveOpens PassiveOpens AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs InErrs OutRsts
Tcp: 1 200 120000 -1 25 4 0 0 1 2529 1520 1 0 9
Udp: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors
Udp: 95 0 0 95 1 4
UdpLite: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors
UdpLite: 0 10 0 0 0 100
""".strip()

PROC_SNMP_NO = """
""".strip()

PROC_SNMP6 = """
Ip6InReceives                   	757
Ip6InHdrErrors                  	0
Ip6InTooBigErrors               	0
Ip6InNoRoutes                   	0
Ip6InAddrErrors                 	0
Ip6InUnknownProtos              	0
Ip6InTruncatedPkts              	0
Ip6InDiscards                   	0
Ip6InDelivers                   	748
Ip6OutForwDatagrams             	0
Ip6OutRequests                  	713
Ip6OutDiscards                  	0
Ip6OutNoRoutes                  	0
Ip6ReasmTimeout                 	0
Ip6ReasmReqds                   	0
Ip6ReasmOKs                     	0
Ip6ReasmFails                   	0
Ip6FragOKs                      	0
Ip6FragFails                    	0
Ip6FragCreates                  	0
Ip6InMcastPkts                  	99
Ip6OutMcastPkts                 	71
Ip6InOctets                     	579410
Ip6OutOctets                    	1553244
Ip6InMcastOctets                	9224
Ip6OutMcastOctets               	5344
Ip6InBcastOctets                	0
Ip6OutBcastOctets               	0
Ip6InNoECTPkts                  	759
Ip6InECT1Pkts                   	0
Ip6InECT0Pkts                   	0
Ip6InCEPkts                     	0
Icmp6InMsgs                     	94
Icmp6InErrors                   	0
Icmp6OutMsgs                    	41
Icmp6OutErrors                  	0
Icmp6InCsumErrors               	0
Icmp6InDestUnreachs             	0
Icmp6InPktTooBigs               	0
Icmp6InTimeExcds                	0
Icmp6InParmProblems             	0
Icmp6InEchos                    	0
Icmp6InEchoReplies              	0
Icmp6InGroupMembQueries         	28
Icmp6InGroupMembResponses       	0
Icmp6InGroupMembReductions      	0
Icmp6InRouterSolicits           	0
Icmp6InRouterAdvertisements     	62
Icmp6InNeighborSolicits         	3
Icmp6InNeighborAdvertisements   	1
Icmp6InRedirects                	0
Icmp6InMLDv2Reports             	0
Icmp6OutDestUnreachs            	0
Icmp6OutPktTooBigs              	0
Icmp6OutTimeExcds               	0
Icmp6OutParmProblems            	0
Icmp6OutEchos                   	0
Icmp6OutEchoReplies             	0
Icmp6OutGroupMembQueries        	0
Icmp6OutGroupMembResponses      	0
Icmp6OutGroupMembReductions     	0
Icmp6OutRouterSolicits          	1
Icmp6OutRouterAdvertisements    	0
Icmp6OutNeighborSolicits        	3
Icmp6OutNeighborAdvertisements  	3
Icmp6OutRedirects               	0
Icmp6OutMLDv2Reports            	34
Icmp6InType130                  	28
Icmp6InType134                  	62
Icmp6InType135                  	3
Icmp6InType136                  	1
Icmp6OutType133                 	1
Icmp6OutType135                 	3
Icmp6OutType136                 	3
Icmp6OutType143                 	34
Udp6InDatagrams                 	0
Udp6NoPorts                     	0
Udp6InErrors                    	0
Udp6OutDatagrams                	0
Udp6RcvbufErrors                	0
Udp6SndbufErrors                	0
Udp6InCsumErrors                	0
UdpLite6InDatagrams             	0
UdpLite6NoPorts                 	0
UdpLite6InErrors                	0
UdpLite6OutDatagrams            	0
UdpLite6RcvbufErrors            	0
UdpLite6SndbufErrors            	0
UdpLite6InCsumErrors            	0
""".strip()

PROC_SNMP6_ODD = """
Ip6InReceives                   	757
Ip6InHdrErrors                  	0
Icmp6OutMLDv2Reports            	0
Icmp6InType130                  	28
Icmp6InType134                  	62
Ip6InDiscards
""".strip()

TCP_STATS_DOC = '''
Ip: Forwarding DefaultTTL InReceives InHdrErrors InAddrErrors ForwDatagrams InUnknownProtos InDiscards InDelivers OutRequests OutDiscards OutNoRoutes ReasmTimeout ReasmReqds ReasmOKs ReasmFails FragOKs FragFails FragCreates
Ip: 2 64 43767 0 0 0 0 0 41807 18407 12 73 0 0 0 10 0 0 0
Icmp: InMsgs InErrors InCsumErrors InDestUnreachs InTimeExcds InParmProbs InSrcQuenchs InRedirects InEchos InEchoReps InTimestamps InTimestampReps InAddrMasks InAddrMaskReps OutMsgs OutErrors OutDestUnreachs OutTimeExcds OutParmProbs OutSrcQuenchs OutRedirects OutEchos OutEchoReps OutTimestamps OutTimestampReps OutAddrMasks OutAddrMaskReps
Icmp: 34 0 0 34 0 0 0 0 0 0 0 0 0 0 44 0 44 0 0 0 0 0 0 0 0 0 0
IcmpMsg: InType3 OutType3
IcmpMsg: 34 44
Tcp: RtoAlgorithm RtoMin RtoMax MaxConn ActiveOpens PassiveOpens AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs InErrs OutRsts InCsumErrors
Tcp: 1 200 120000 -1 444 0 0 6 7 19269 17050 5 4 234 0
Udp: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors InCsumErrors IgnoredMulti
Udp: 18905 34 0 1348 0 0 0 3565
UdpLite: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors InCsumErrors IgnoredMulti
UdpLite: 0 0 0 0 0 0 0 0
'''.strip()

TCP_IP_STATS_IPV6_DOC = '''
Ip6InReceives                   	757
Ip6InHdrErrors                  	0
Ip6InTooBigErrors               	0
Ip6InNoRoutes                   	0
Ip6InAddrErrors                 	0
Ip6InDiscards                       10
Ip6OutForwDatagrams             	0
Ip6OutDiscards                  	0
Ip6OutNoRoutes                  	0
Ip6InOctets                     	579410
Icmp6OutErrors                  	0
Icmp6InCsumErrors               	0
'''.strip()

SNMPD_CONF = """
#       sec.name  source          community
com2sec notConfigUser  default       public

#       groupName      securityModel securityName
group   notConfigGroup v1           notConfigUser
group   notConfigGroup v2c           notConfigUser

# Make at least  snmpwalk -v 1 localhost -c public system fast again.
#       name           incl/excl     subtree         mask(optional)
view    systemview    included   .1.3.6.1.2.1.1
view    systemview    included   .1.3.6.1.2.1.25.1.1

#       group          context sec.model sec.level prefix read   write  notif
access  notConfigGroup ""      any       noauth    exact  systemview none none

dontLogTCPWrappersConnects yes
include_ifmib_iface_prefix eth enp1s0
leave_pidfile

syscontact Root <root@localhost> (configure /etc/snmp/snmp.local.conf)
""".strip()

SNMPD_CONF_NO_HIT = """
#       sec.name  source          community
""".strip()

SNMPD_CONF_EMPTY = """
""".strip()


def test_snmp():
    stats = TcpIpStats(context_wrap(PROC_SNMP))
    snmp_stats = stats.get("Ip")
    assert snmp_stats
    assert snmp_stats["DefaultTTL"] == 64
    assert snmp_stats["InReceives"] == 2628
    assert snmp_stats["InHdrErrors"] == 0
    assert snmp_stats["InAddrErrors"] == 2
    assert snmp_stats["InDiscards"] == 0
    assert snmp_stats["InDelivers"] == 2624
    assert snmp_stats["ReasmFails"] == 10
    assert snmp_stats["OutRequests"] == 1618

    snmp_stats = stats.get("Tcp")
    assert snmp_stats["RtoMax"] == 120000
    assert snmp_stats["MaxConn"] == -1
    assert snmp_stats["OutSegs"] == 1520
    assert snmp_stats["ActiveOpens"] == 25

    snmp_stats = stats.get("IcmpMsg")
    assert snmp_stats["OutType3"] == 44

    snmp_stats = stats.get("Udp")
    assert snmp_stats["OutDatagrams"] == 95
    assert snmp_stats["RcvbufErrors"] == 1
    assert snmp_stats["NoPorts"] == 0

    stats = TcpIpStats(context_wrap(PROC_SNMP_NO))
    snmp_stats = stats.get("Ip")
    assert snmp_stats is None


def test_snmp6():
    stats = TcpIpStatsIPV6(context_wrap(PROC_SNMP6))
    snmp6_stats_RX = stats.get("Ip6InReceives")
    snmp6_stats_MLD = stats.get("Icmp6OutMLDv2Reports")
    assert snmp6_stats_RX == 757
    assert snmp6_stats_MLD == 34
    stats = TcpIpStatsIPV6(context_wrap(PROC_SNMP6_ODD))
    snmp6_stats_disx = stats.get("Ip6InDiscards")
    snmp6_stats_odd = stats.get("some_unknown")
    assert snmp6_stats_disx is None
    assert snmp6_stats_odd is None


def test_snmpd_conf():
    result = SnmpdConf(context_wrap(SNMPD_CONF))
    assert len(result) == 8
    assert 'com2sec' in result
    assert result['group'][0] == 'notConfigGroup v1           notConfigUser'
    assert result['group'][1] == 'notConfigGroup v2c           notConfigUser'
    assert result['leave_pidfile'] == []
    assert result['access'] == ['notConfigGroup ""      any       noauth    exact  systemview none none']
    assert result['syscontact'] == ['Root <root@localhost> (configure /etc/snmp/snmp.local.conf)']


def test_snmpd_conf_empty():
    with pytest.raises(ParseException) as exc:
        SnmpdConf(context_wrap(SNMPD_CONF_EMPTY))
    assert str(exc.value) == "Empty Content"


def test_snmpd_conf_empty2():
    with pytest.raises(ParseException) as exc:
        SnmpdConf(context_wrap(SNMPD_CONF_NO_HIT))
    assert str(exc.value) == "Empty Content"


def test_doc():
    env = {
        'proc_snmp_ipv4': TcpIpStats(context_wrap(TCP_STATS_DOC)),
        'proc_snmp_ipv6': TcpIpStatsIPV6(context_wrap(TCP_IP_STATS_IPV6_DOC)),
        'snmpd_conf': SnmpdConf(context_wrap(SNMPD_CONF)),
    }
    failed, total = doctest.testmod(snmp, globs=env)
    assert failed == 0
