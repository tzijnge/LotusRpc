#include <cstddef>
#include <type_traits>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "TestUtils.hpp"
#include "generated/RetrieveDefinition/RetrieveDefinition.hpp"

class MockRetrieveDefinitionS0 : public test_rd::srv0_shim
{
public:
    MOCK_METHOD(void, f0, (), (override));
};

namespace
{
    constexpr size_t DefStreamPacketOverhead{5};
    constexpr size_t TxBufferSize{test_rd::lrpc_meta::DefinitionStreamChunkSize + DefStreamPacketOverhead};
    constexpr size_t ChunkPayloadSize{TxBufferSize - DefStreamPacketOverhead};
    constexpr size_t CompressedDefSize{test_rd::lrpc_meta::CompressedDefinition.size()};
    constexpr size_t HexDigitsPerByte{2};
    constexpr size_t TxBufferSizeHex{TxBufferSize * HexDigitsPerByte};

    static_assert(
        std::is_same<test_rd::RetrieveDefinition, lrpc::Server<0, test_rd::LrpcMeta_service, 256, TxBufferSize>>::value,
        "Definition not as expected");
    static_assert(CompressedDefSize == 432, "Compressed definition size not as expected");

    constexpr size_t NumberFullPackets{CompressedDefSize / ChunkPayloadSize};
    constexpr size_t LastPacketPayloadSize{CompressedDefSize % ChunkPayloadSize};
    constexpr size_t LastPacketTotalSize{DefStreamPacketOverhead + LastPacketPayloadSize};
    constexpr size_t LastPacketSizeHex{LastPacketTotalSize * HexDigitsPerByte};
    constexpr size_t TotalResponseSizeHex{(NumberFullPackets * TxBufferSizeHex) + LastPacketSizeHex};
}

using TestRetrieveDefinition = testutils::TestServerBase<test_rd::RetrieveDefinition, MockRetrieveDefinitionS0, false>;

// definition has a length of 432 bytes in compressed form
// definition stream message from server to client has an overhead of
// 5 bytes per chunk: message length, service ID, stream ID, chunk size, 'final' param
// TX buffer size has been chosen in the definition as 112 bytes.
// This leaves 112 - 5 = 107 bytes for the chunk payload. This means
// that the compressed definition is transferred from server to client
// in 4 full packets (107 bytes each) and 1 partial packet (4 bytes)
//
// To update after re-running lrpcg on TestRetrieveDefinition.lrpc.yaml:
//   1. Read tests/cpp/generated/RetrieveDefinition/LrpcMeta_constants.hpp
//   2. Update the static_assert on line 25 with the new CompressedDefinition.size()
//   3. All packet counts, sizes, and hex strings in the test body are derived from
//      the constants above — they update automatically. The only hard-coded hex
//      values that may need manual updating are:
//        - response.substr(8, 20): first 10 bytes of the compressed definition payload
//          (bytes 4-13 of the first packet). Read them from CompressedDefinition[0..9]
//          in LrpcMeta_constants.hpp and format as uppercase hex.
//        - "6FFF01": length byte (TxBufferSize-1), service 0xFF, stream 0x01 — only
//          changes if TxBufferSize changes in the definition settings.
//        - "6B": chunk payload size in hex (107 = 0x6B) — only changes if TxBufferSize
//          changes in the definition settings.
//        - "08FF01" and "04": length byte and payload size of the partial last packet.
//          Recompute as: length = DefStreamPacketOverhead + LastPacketPayloadSize - 1,
//          payload size = CompressedDefSize % ChunkPayloadSize. If the new definition
//          divides evenly (remainder 0), remove the partial-packet block entirely.

TEST_F(TestRetrieveDefinition, retrieveDefinition)
{
    const auto response = receive("02FF01");
    ASSERT_EQ(TotalResponseSizeHex, response.size());

    // sanity check on first 10 bytes
    EXPECT_EQ("FD377A585A000004E6D6", response.substr(8, 20));

    for (size_t i = 0; i < NumberFullPackets; ++i)
    {
        const size_t start = i * TxBufferSizeHex;
        const auto message = response.substr(start, TxBufferSizeHex);

        // length, service ID and stream ID
        EXPECT_EQ("6FFF01", message.substr(0, 6));
        // bytearray length
        EXPECT_EQ("6B", message.substr(6, 2));
        // not final
        EXPECT_EQ("00", message.substr(TxBufferSizeHex - HexDigitsPerByte, HexDigitsPerByte));
    }

    // partial last packet
    const size_t start = NumberFullPackets * TxBufferSizeHex;
    const auto message = response.substr(start, LastPacketSizeHex);

    // length, service ID and stream ID
    EXPECT_EQ("08FF01", message.substr(0, 6));
    // bytearray length (4 remaining bytes)
    EXPECT_EQ("04", message.substr(6, 2));
    // final
    EXPECT_EQ("01", message.substr(LastPacketSizeHex - HexDigitsPerByte, HexDigitsPerByte));
}