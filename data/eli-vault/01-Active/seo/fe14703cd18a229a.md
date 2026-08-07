---
id: fe14703cd18a229a
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: ["tool", "code"]
containmentHash: 81e6a7c4bb96f6acf3dd
createdAt: 1786051357025
embeddingSig: "artesaos:seotools:facades|facades:jsonld:with|facades:jsonldmulti:artesaos|facades:twittercard:artesaos|graph:artesaos:seotools|jsonld:with:multi|multi:artesaos:seotools|seotools:facades:jsonld|seotools:facades:jsonldmulti|seotools:facades:twittercard|twittercard:artesaos:seotools|with:multi:artesaos"
---
Graph;
use Artesaos\SEOTools\Facades\TwitterCard;
use Artesaos\SEOTools\Facades\JsonLd;
// OR with multi
use Artesaos\SEOTools\Facades\JsonLdMulti;
// OR
use Artesaos\SEOTools\Facades\SEOTools;

class CommonController extends Controller
{
    public function index()
    {
        SEOMeta::setTitle('Home');
        SEOMeta::setDescription('This is my page description');