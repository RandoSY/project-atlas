#ifndef ATLAS_LAB_PROTOCOL_H
#define ATLAS_LAB_PROTOCOL_H
#include <stdint.h>
#define LAB_SYNC 0xA5
#define LAB_VERSION 1
#define LAB_MAX_PAYLOAD 8
#define LAB_FRAME_MAX 15
#define LAB_IDENTIFY 0x01
#define LAB_ADC_START 0x10
#define LAB_ADC_READ 0x11
#define LAB_TIMER_START 0x20
#define LAB_TIMER_READ 0x21
#define LAB_STATUS 0x30
#define LAB_CLEAR 0x31
#define LAB_OK 0
#define LAB_BUSY 1
#define LAB_NOT_READY 2
#define LAB_BAD_ARGUMENT 3
#define LAB_UNSUPPORTED 4
#define LAB_FAULT 5
struct lab_request { uint8_t seq, op, len, data[LAB_MAX_PAYLOAD]; };
struct lab_parser { uint8_t bytes[LAB_FRAME_MAX]; uint8_t used; uint16_t errors; };
uint16_t lab_crc(const uint8_t *data, uint8_t len);
uint8_t lab_pack(uint8_t seq, uint8_t op, const uint8_t *data, uint8_t len, uint8_t *out);
uint8_t lab_feed(struct lab_parser *parser, uint8_t byte, struct lab_request *request);
#endif
