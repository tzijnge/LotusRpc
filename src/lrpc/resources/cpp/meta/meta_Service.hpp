#pragma once
#include "meta_ServiceShim.hpp"

namespace lrpc
{
    class MetaService : public lrpc::metaServiceShim
    {
    public:
        std::tuple<uint32_t, uint32_t, uint32_t, uint32_t> error(uint32_t type) override
        {
            return {type, 0, 0, 0};
        }
    };
}