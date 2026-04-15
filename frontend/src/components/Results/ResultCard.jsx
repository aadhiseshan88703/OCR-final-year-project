import React, { useState } from 'react';
import {
  ChevronDown, ChevronUp, CheckCircle, AlertTriangle,
  FileText, Code, ReceiptText, Hash, Calendar, Phone,
  IndianRupee, ShoppingCart, Percent,
} from 'lucide-react';
import JsonViewer from './JsonViewer';

// ── Invoice fields renderer ───────────────────────────────────────────────────
const FIELD_META = [
  { key: 'invoice_no',  label: 'Invoice No.',   Icon: Hash,         color: 'blue'   },
  { key: 'date',        label: 'Date',           Icon: Calendar,     color: 'violet' },
  { key: 'phone',       label: 'Phone',          Icon: Phone,        color: 'sky'    },
  { key: 'sub_total',   label: 'Sub Total',      Icon: ShoppingCart, color: 'amber'  },
  { key: 'tax',         label: 'Tax / GST',      Icon: Percent,      color: 'orange' },
  { key: 'grand_total', label: 'Grand Total',    Icon: IndianRupee,  color: 'green'  },
];

const COLOR_MAP = {
  blue:   { bg: 'bg-blue-50',   icon: 'text-blue-500',   label: 'text-blue-700',   value: 'text-blue-900'   },
  violet: { bg: 'bg-violet-50', icon: 'text-violet-500', label: 'text-violet-700', value: 'text-violet-900' },
  sky:    { bg: 'bg-sky-50',    icon: 'text-sky-500',    label: 'text-sky-700',    value: 'text-sky-900'    },
  amber:  { bg: 'bg-amber-50',  icon: 'text-amber-500',  label: 'text-amber-700',  value: 'text-amber-900'  },
  orange: { bg: 'bg-orange-50', icon: 'text-orange-500', label: 'text-orange-700', value: 'text-orange-900' },
  green:  { bg: 'bg-green-50',  icon: 'text-green-500',  label: 'text-green-700',  value: 'text-green-900'  },
};

const InvoiceFields = ({ fields }) => {
  const hasAny = fields && Object.values(fields).some((v) => v !== null && v !== undefined);
  if (!hasAny) {
    return (
      <p className="text-gray-400 text-center italic py-10">
        No structured invoice fields could be extracted from this image.
      </p>
    );
  }
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {FIELD_META.map(({ key, label, Icon, color }) => {
        const val = fields?.[key];
        if (val === null || val === undefined) return null;
        const cls = COLOR_MAP[color];
        return (
          <div
            key={key}
            className={`flex items-start gap-3 p-4 rounded-xl border border-gray-100 ${cls.bg} shadow-sm`}
          >
            <div className={`mt-0.5 flex-shrink-0 ${cls.icon}`}>
              <Icon size={20} />
            </div>
            <div className="min-w-0">
              <p className={`text-xs font-semibold uppercase tracking-wide ${cls.label}`}>{label}</p>
              <p className={`text-base font-bold mt-0.5 break-all ${cls.value}`}>
                {typeof val === 'number'
                  ? val.toLocaleString('en-IN', { maximumFractionDigits: 2 })
                  : String(val)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ── Language summary badge ────────────────────────────────────────────────────
const LanguageBadges = ({ structuredData }) => {
  const detected = structuredData?.language_summary?.detected;
  if (!detected || detected.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2 px-6 py-3 border-b border-gray-100 bg-slate-50">
      {detected.map((lang) => (
        <span
          key={lang.language}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700 border border-indigo-200"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 inline-block" />
          {lang.language}
          <span className="text-indigo-400 font-normal">
            ({Math.round(lang.avg_confidence * 100)}%)
          </span>
        </span>
      ))}
    </div>
  );
};

// ── Main ResultCard ───────────────────────────────────────────────────────────
const TABS = [
  { id: 'text',   label: 'Extracted Text',  Icon: FileText      },
  { id: 'fields', label: 'Invoice Fields',  Icon: ReceiptText   },
  { id: 'json',   label: 'Structured JSON', Icon: Code          },
];

const ResultCard = ({ result }) => {
  const [activeTab, setActiveTab] = useState('text');
  const [isExpanded, setIsExpanded] = useState(true);

  const isSuccess = result.status === 'success';

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-6 transition-all">
      {/* Header */}
      <div
        className="bg-gray-50 border-b border-gray-200 px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-sm flex-shrink-0">
            {result.image_number}
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">{result.image_name}</h4>
            <div className="flex items-center gap-2 mt-1">
              {isSuccess ? (
                <span className="flex items-center gap-1 text-xs font-medium text-green-600">
                  <CheckCircle size={14} /> Processed Successfully
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs font-medium text-red-600">
                  <AlertTriangle size={14} /> Processing Failed
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="text-gray-400">
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-0">
          {!isSuccess ? (
            <div className="p-6 bg-red-50 text-red-700">
              {result.error && (
                <p className="font-semibold text-red-800 mb-2 flex items-center gap-2">
                  <AlertTriangle className="flex-shrink-0" size={18} />
                  {result.error}
                </p>
              )}
              <p className="text-sm flex items-start gap-2 text-red-600">
                <AlertTriangle className="flex-shrink-0 mt-0.5" size={16} />
                <span>{result.error_message || 'Unknown error occurred during processing.'}</span>
              </p>
            </div>
          ) : (
            <>
              {/* Language badges */}
              <LanguageBadges structuredData={result.structured_data} />

              {/* Tab bar */}
              <div className="border-b border-gray-200 px-6 pt-4 flex gap-6 overflow-x-auto">
                {TABS.map(({ id, label, Icon }) => (
                  <button
                    key={id}
                    className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 whitespace-nowrap ${
                      activeTab === id
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab(id)}
                  >
                    <Icon size={16} />
                    {label}
                  </button>
                ))}
              </div>

              <div className="p-6 bg-gray-50">
                {/* ── Extracted Text ── */}
                {activeTab === 'text' && (
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-inner">
                    {result.extracted_text ? (
                      <pre className="whitespace-pre font-mono text-sm text-gray-800 break-words max-h-[500px] overflow-auto custom-scrollbar leading-relaxed">
                        {result.extracted_text}
                      </pre>
                    ) : (
                      <p className="text-gray-500 text-center italic py-8">
                        No text extracted from this image.
                      </p>
                    )}
                  </div>
                )}

                {/* ── Invoice Fields ── */}
                {activeTab === 'fields' && (
                  <InvoiceFields fields={result.structured_data?.invoice_fields} />
                )}

                {/* ── Structured JSON ── */}
                {activeTab === 'json' && (
                  <JsonViewer data={result.structured_data || {}} />
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ResultCard;
