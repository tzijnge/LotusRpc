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
        ((this)->*(invokers.at(messageId)))(reader, writer);
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
    void invokeF0(Reader &r, Writer &w)
    {
        f0();
    }

    void invokeF1(Reader &r, Writer &w)
    {
        f1();
    }

    void invokeF2(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint8_t>(r);
        f2(a);
    }

    void invokeF3(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint16_t>(r);
        f3(a);
    }

    void invokeF4(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<float>(r);
        f4(a);
    }

    void invokeF5(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint16_t, 2>(r);
        f5(a);
    }

    void invokeF6(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<etl::string_view>(r);
        f6(a);
    }

    void invokeF7(Reader &r, Writer &w)
    {
        const auto cd = etl::read_unchecked<CompositeData>(r);
        f7(cd);
    }

    void invokeF8(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<MyEnum>(r);
        f8(a);
    }

    void invokeF9(Reader &r, Writer &w)
    {
        auto a = etl::read_unchecked<CompositeData2, 2>(r);
        f9(a);
    }

    void invokeF10(Reader &r, Writer &w)
    {
        const auto cd3 = etl::read_unchecked<CompositeData3>(r);
        f10(cd3);
    }

    void invokef11(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint8_t>(r);
        const auto b = etl::read_unchecked<uint8_t>(r);
        f11(a, b);
    }

    void invokef12(Reader &r, Writer &w)
    {
        const auto response = f12();
        etl::write_unchecked<uint8_t>(w, response);
    }

    void invokef13(Reader &r, Writer &w)
    {
        const auto response = f13();
        etl::write_unchecked<uint16_t>(w, response);
    }

    void invokef14(Reader &r, Writer &w)
    {
        const auto response = f14();
        etl::write_unchecked<float>(w, response);
    }

    void invokef15(Reader &r, Writer &w)
    {
        const auto response = f15();
        w.write_unchecked<const uint16_t>(response);
    }

    void invokef16(Reader &r, Writer &w)
    {
        const auto response = f16();
        etl::write_unchecked<etl::string_view>(w, response);
    }

    void invokef17(Reader &r, Writer &w)
    {
        const auto response = f17();
        etl::write_unchecked<CompositeData>(w, response);
    }

    void invokef18(Reader &r, Writer &w)
    {
        const auto response = f18();
        etl::write_unchecked<MyEnum>(w, response);
    }

    void invokef19(Reader &r, Writer &w)
    {
        const auto response = f19();
        etl::write_unchecked<const CompositeData2>(w, response);
    }

    void invokef20(Reader &r, Writer &w)
    {
        const auto response = f20();
        etl::write_unchecked<CompositeData3>(w, response);
    }

    void invokef21(Reader &r, Writer &w)
    {
        const auto response = f21();
        etl::write_unchecked<uint8_t>(w, std::get<0>(response));
        etl::write_unchecked<uint8_t>(w, std::get<1>(response));
    }

    void invokef22(Reader &r, Writer &w)
    {
        const auto a1 = etl::read_unchecked<etl::string_view>(r);
        const auto a2 = etl::read_unchecked<etl::string_view>(r);
        const auto response = f22(a1, a2);
        etl::write_unchecked<etl::string_view>(w, std::get<0>(response));
        etl::write_unchecked<etl::string_view>(w, std::get<1>(response));
    }

    using Invoker = void (I0DecoderShim::*)(Reader &reader, Writer &writer);
    inline static const etl::array invokers{
        &I0DecoderShim::invokeF0,
        &I0DecoderShim::invokeF1,
        &I0DecoderShim::invokeF2,
        &I0DecoderShim::invokeF3,
        &I0DecoderShim::invokeF4,
        &I0DecoderShim::invokeF5,
        &I0DecoderShim::invokeF6,
        &I0DecoderShim::invokeF7,
        &I0DecoderShim::invokeF8,
        &I0DecoderShim::invokeF9,
        &I0DecoderShim::invokeF10,
        &I0DecoderShim::invokef11,
        &I0DecoderShim::invokef12,
        &I0DecoderShim::invokef13,
        &I0DecoderShim::invokef14,
        &I0DecoderShim::invokef15,
        &I0DecoderShim::invokef16,
        &I0DecoderShim::invokef17,
        &I0DecoderShim::invokef18,
        &I0DecoderShim::invokef19,
        &I0DecoderShim::invokef20,
        &I0DecoderShim::invokef21,
        &I0DecoderShim::invokef22,
    };
};