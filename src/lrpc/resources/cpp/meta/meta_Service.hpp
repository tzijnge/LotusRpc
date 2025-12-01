#pragma once
#include "meta_ServiceShim.hpp"

namespace lrpc
{
    class MetaService : public lrpc::metaServiceShim
    {
    public:
        void error() override {};
        void error_stop() override {};
    };
}