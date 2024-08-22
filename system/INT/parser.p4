/* -*- P4_16 -*- */
#include "header.p4"
#include <core.p4>
#include <v1model.p4>

parser ParserImpl(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    @name("start")
    state start {
        transition parse_ethernet;
    }
    @name("parse_ethernet")
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x0800: parse_ipv4;
            16w0x0806: parse_arp;
            default: accept;
        }
    }
    @name("parse_arp")
    state parse_arp {
        packet.extract(hdr.arp);
        transition accept;
    }
    @name("parse_ipv4")
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w0x11:parse_udp;
            default:accept;
        }
    }
    @name("parse_udp")
    state parse_udp {
        packet.extract(hdr.udp);
        transition select(hdr.udp.dstPort) {
            16w0x08AE:parse_sr;      // port 2222
            default:accept;
        }
    }
    @name("parse_sr")
    state parse_sr {
        packet.extract(hdr.sr);
        transition accept;
    }
}



control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.udp);
        packet.emit(hdr.sr);
        packet.emit(hdr.device_no);
        packet.emit(hdr.ingress_port);
        packet.emit(hdr.egress_port);
        packet.emit(hdr.ingress_global_timestamp);
        packet.emit(hdr.egress_global_timestamp);
        packet.emit(hdr.enq_qdepth);
        packet.emit(hdr.deq_qdepth);
        packet.emit(hdr.ingress_byte_count);
        packet.emit(hdr.egress_byte_count);
    }
    }

control verifyChecksum(inout headers hdr, inout metadata meta) {
    apply {
        // Add checksum verification code here
    }
}

control computeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        update_checksum(
        hdr.ipv4.isValid(),
           { hdr.ipv4.version,
             hdr.ipv4.ihl,
             hdr.ipv4.diffserv,
             hdr.ipv4.totalLen,
             hdr.ipv4.identification,
             hdr.ipv4.flags,
             hdr.ipv4.fragOffset,
             hdr.ipv4.ttl,
             hdr.ipv4.protocol,
             hdr.ipv4.srcAddr,
             hdr.ipv4.dstAddr },
           hdr.ipv4.hdrChecksum,
           HashAlgorithm.csum16);

   }
}
