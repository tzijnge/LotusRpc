#include "generated/RetrieveDefinition/RetrieveDefinition.hpp"
#include "TestUtils.hpp"

namespace
{
    class Mockservice : public test_rd::s0_shim
    {
    public:
        MOCK_METHOD(void, f0, (), (override));
    };

    constexpr size_t TxBufferSize{47};
    constexpr size_t DefStreamPacketOverhead{5};
    constexpr size_t CompressedDefSize{test_rd::lrpc_meta::CompressedDefinition.size()};
    constexpr size_t HexDigitsPerByte{2};
    constexpr size_t TxBufferSizeHex{TxBufferSize * HexDigitsPerByte};

    static_assert(std::is_same<test_rd::RetrieveDefinition, lrpc::Server<0, test_rd::LrpcMeta_service, 256, TxBufferSize>>::value, "Definition not as expected");
    static_assert(CompressedDefSize == 420);
    static_assert((CompressedDefSize % (TxBufferSize - DefStreamPacketOverhead)) == 0);

    constexpr size_t NumberDefStreamPackets{CompressedDefSize / (TxBufferSize - DefStreamPacketOverhead)};
}

using TestRetrieveDefinition = testutils::TestServerBase<test_rd::RetrieveDefinition, Mockservice, false>;

// definition has a length of 420 bytes in compressed form
// definition stream message from server to client has an overhead of
// 5 bytes per chunk: message length, service ID, stream ID, chunk size, 'final' param
// TX buffer size has been chosen in the definition as 47 bytes.
// This leaves 47 - 5 = 42 bytes for the chunk payload. This means
// that the compressed definition is transferred from server to client
// in 420 / 42 = 10 packets

TEST_F(TestRetrieveDefinition, retrieveDefinition)
{
    const auto response = receive("03FF01");
    ASSERT_EQ(NumberDefStreamPackets * TxBufferSizeHex, response.size());

    // sanity check on first 10 bytes
    EXPECT_EQ("FD377A585A000004E6D6", response.substr(8, 20));

    for (size_t i = 0; i < NumberDefStreamPackets; ++i)
    {
        const size_t start = i * TxBufferSizeHex;
        const auto message = response.substr(start, TxBufferSizeHex);

        // length, service ID and message ID
        EXPECT_EQ("2FFF01", message.substr(0, 6));
        // bytearray length
        EXPECT_EQ("2A", message.substr(6, 2));

        // final parameter
        if (i == (NumberDefStreamPackets - 1))
        {
            EXPECT_EQ("01", message.substr(TxBufferSizeHex - HexDigitsPerByte, HexDigitsPerByte));
        }
        else
        {
            EXPECT_EQ("00", message.substr(TxBufferSizeHex - HexDigitsPerByte, HexDigitsPerByte));
        }
    }
}