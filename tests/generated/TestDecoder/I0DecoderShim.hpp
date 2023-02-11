#pragma once
#include "Decoder.hpp"
#include "EtlRwExtensions.hpp"
#include "TestDecoder_all.hpp"
#include <etl/string_view.h>
#include <etl/span.h>


class I0DecoderShim : public Decoder
{
public:
    uint32_t id() const override { return 0; }

    void decode(Reader &reader, Writer &writer) override
    {
        auto messageId = reader.read_unchecked<uint8_t>();
        ((this)->*(functionShims.at(messageId)))(reader, writer);
    }

protected:
    virtual void f0() = 0;
    virtual void f1() = 0;
    virtual void f2(uint8_t a) = 0;
    virtual void f3(uint16_t a) = 0;
    virtual void f4(float a) = 0;
    virtual void f5(const etl::span<const uint16_t> &a) = 0;
    virtual void f6(const etl::string_view &a) = 0;
    virtual void f7(const CompositeData &a) = 0;
    virtual void f8(MyEnum a) = 0;
    virtual void f9(const etl::span<const CompositeData2> &a) = 0;
    virtual void f10(const CompositeData3 &a) = 0;
    virtual void f11(uint8_t a, uint8_t b) = 0;
    virtual uint8_t f12() = 0;
    virtual uint16_t f13() = 0;
    virtual float f14() = 0;
    virtual etl::span<const uint16_t> f15() = 0;
    virtual etl::string_view f16() = 0;
    virtual CompositeData f17() = 0;
    virtual MyEnum f18() = 0;
    virtual etl::span<const CompositeData2> f19() = 0;
    virtual CompositeData3 f20() = 0;
    virtual std::tuple<uint8_t, uint8_t> f21() = 0;
    virtual std::tuple<etl::string_view, etl::string_view> f22(const etl::string_view &s1, const etl::string_view &s2) = 0;

private:
    void f0_shim(Reader &r, Writer &w)
    {
        f0();
    }

    void f1_shim(Reader &r, Writer &w)
    {
        f1();
    }

    void f2_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint8_t>(r);
        f2(a);
    }

    void f3_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint16_t>(r);
        f3(a);
    }

    void f4_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<float>(r);
        f4(a);
    }

    void f5_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint16_t, 2>(r);
        f5(a);
    }

    void f6_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<etl::string_view>(r);
        f6(a);
    }

    void f7_shim(Reader &r, Writer &w)
    {
        const auto cd = etl::read_unchecked<CompositeData>(r);
        f7(cd);
    }

    void f8_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<MyEnum>(r);
        f8(a);
    }

    void f9_shim(Reader &r, Writer &w)
    {
        auto a = etl::read_unchecked<CompositeData2, 2>(r);
        f9(a);
    }

    void f10_shim(Reader &r, Writer &w)
    {
        const auto cd3 = etl::read_unchecked<CompositeData3>(r);
        f10(cd3);
    }

    void f11_shim(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint8_t>(r);
        const auto b = etl::read_unchecked<uint8_t>(r);
        f11(a, b);
    }

    void f12_shim(Reader &r, Writer &w)
    {
        const auto response = f12();
        etl::write_unchecked<uint8_t>(w, response);
    }

    void f13_shim(Reader &r, Writer &w)
    {
        const auto response = f13();
        etl::write_unchecked<uint16_t>(w, response);
    }

    void f14_shim(Reader &r, Writer &w)
    {
        const auto response = f14();
        etl::write_unchecked<float>(w, response);
    }

    void f15_shim(Reader &r, Writer &w)
    {
        const auto response = f15();
        w.write_unchecked<const uint16_t>(response);
    }

    void f16_shim(Reader &r, Writer &w)
    {
        const auto response = f16();
        etl::write_unchecked<etl::string_view>(w, response);
    }

    void f17_shim(Reader &r, Writer &w)
    {
        const auto response = f17();
        etl::write_unchecked<CompositeData>(w, response);
    }

    void f18_shim(Reader &r, Writer &w)
    {
        const auto response = f18();
        etl::write_unchecked<MyEnum>(w, response);
    }

    void f19_shim(Reader &r, Writer &w)
    {
        const auto response = f19();
        etl::write_unchecked<const CompositeData2>(w, response);
    }

    void f20_shim(Reader &r, Writer &w)
    {
        const auto response = f20();
        etl::write_unchecked<CompositeData3>(w, response);
    }

    void f21_shim(Reader &r, Writer &w)
    {
        const auto response = f21();
        etl::write_unchecked<uint8_t>(w, std::get<0>(response));
        etl::write_unchecked<uint8_t>(w, std::get<1>(response));
    }

    void f22_shim(Reader &r, Writer &w)
    {
        const auto a1 = etl::read_unchecked<etl::string_view>(r);
        const auto a2 = etl::read_unchecked<etl::string_view>(r);
        const auto response = f22(a1, a2);
        etl::write_unchecked<etl::string_view>(w, std::get<0>(response));
        etl::write_unchecked<etl::string_view>(w, std::get<1>(response));
    }

    inline static const etl::array functionShims{
        &I0DecoderShim::f0_shim,
        &I0DecoderShim::f1_shim,
        &I0DecoderShim::f2_shim,
        &I0DecoderShim::f3_shim,
        &I0DecoderShim::f4_shim,
        &I0DecoderShim::f5_shim,
        &I0DecoderShim::f6_shim,
        &I0DecoderShim::f7_shim,
        &I0DecoderShim::f8_shim,
        &I0DecoderShim::f9_shim,
        &I0DecoderShim::f10_shim,
        &I0DecoderShim::f11_shim,
        &I0DecoderShim::f12_shim,
        &I0DecoderShim::f13_shim,
        &I0DecoderShim::f14_shim,
        &I0DecoderShim::f15_shim,
        &I0DecoderShim::f16_shim,
        &I0DecoderShim::f17_shim,
        &I0DecoderShim::f18_shim,
        &I0DecoderShim::f19_shim,
        &I0DecoderShim::f20_shim,
        &I0DecoderShim::f21_shim,
        &I0DecoderShim::f22_shim,
    };
};